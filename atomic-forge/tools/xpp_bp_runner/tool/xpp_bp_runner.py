import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class XppBpRunnerToolInputSchema(BaseIOSchema):
    """
    Tool for running Microsoft's X++ Best Practice analyzer (xppbp.exe) over
    a D365 F&O metadata folder and a model name. Returns structured BP
    findings (rule, severity, file, line, message) parsed from the XML log.

    The tool ships a graceful no-op path for environments where xppbp.exe is
    not installed (e.g. Linux CI runners, developer laptops without a D365
    dev VM): instead of raising, it returns a structured output with
    `tool_available=false` and a `details` message. Use the `available()`
    helper or the output `tool_available` flag to branch in agent pipelines.
    """

    metadata_path: str = Field(
        ...,
        description="Path to the D365 packages/metadata folder (the local equivalent of c:\\packages).",
    )
    model_name: str = Field(..., description="Name of the model to analyze (e.g. 'ApplicationFoundation', 'YourCustomModel').")
    generate_car: bool = Field(
        default=False,
        description="Also generate the Customization Analysis Report (CAR). Adds runtime but produces upgrade-readiness output.",
    )
    extra_args: List[str] = Field(
        default_factory=list,
        description="Additional command-line args to pass to xppbp.exe verbatim.",
    )
    timeout_seconds: int = Field(
        default=600, ge=10, description="Subprocess timeout. Long BP runs on large models can exceed the default."
    )


#################
# OUTPUT SCHEMA #
#################
class BpFinding(BaseIOSchema):
    """A single Best Practice finding parsed from the xppbp XML log."""

    rule: str = Field(..., description="BP rule identifier (e.g. 'BPCheckObjectMustBeBuilt', 'BPHardcoded...').")
    severity: str = Field(..., description="Severity ('Error', 'Warning', 'Info', or empty if not reported).")
    file_path: Optional[str] = Field(default=None, description="File the finding applies to, if reported.")
    line_number: Optional[int] = Field(default=None, description="Line number in the file, if reported.")
    message: str = Field(..., description="Human-readable description of the BP violation.")


class XppBpRunnerToolOutputSchema(BaseIOSchema):
    """Schema for the output of the XppBpRunnerTool."""

    tool_available: bool = Field(
        ..., description="True if xppbp.exe was found and executed. False on Linux/CI or when not installed."
    )
    return_code: Optional[int] = Field(
        default=None, description="Exit code from xppbp.exe. None when tool_available is False."
    )
    findings: List[BpFinding] = Field(
        default_factory=list, description="Parsed BP findings from the XML log. Empty if the tool was unavailable."
    )
    log_xml_path: Optional[str] = Field(
        default=None, description="Path to the produced XML log, when the tool ran. Useful for follow-up inspection."
    )
    car_path: Optional[str] = Field(
        default=None, description="Path to the produced CAR report, when generate_car was True and the run succeeded."
    )
    details: str = Field(
        ..., description="Human-readable summary or error description (e.g. why tool_available is False)."
    )


#################
# CONFIGURATION #
#################
class XppBpRunnerToolConfig(BaseToolConfig):
    """
    Configuration for the XppBpRunnerTool.

    Attributes:
        xppbp_path: Explicit path to xppbp.exe. If None, the tool searches PATH and a set of
            well-known D365 dev VM locations.
        extra_search_paths: Additional directories to probe for xppbp.exe.
    """

    xppbp_path: Optional[str] = None
    extra_search_paths: List[str] = []


# Common D365 dev VM locations. Order matters — first hit wins.
_DEFAULT_SEARCH_PATHS = (
    r"C:\packages\bin",
    r"C:\AOSService\PackagesLocalDirectory\bin",
    r"K:\AosService\PackagesLocalDirectory\bin",
    r"J:\AosService\PackagesLocalDirectory\bin",
)


#####################
# MAIN TOOL & LOGIC #
#####################
class XppBpRunnerTool(BaseTool[XppBpRunnerToolInputSchema, XppBpRunnerToolOutputSchema]):
    """Run Microsoft's X++ Best Practice analyzer and parse the XML log."""

    def __init__(self, config: XppBpRunnerToolConfig = XppBpRunnerToolConfig()):
        super().__init__(config)
        self._explicit_path = config.xppbp_path
        self._extra_search_paths = list(config.extra_search_paths)

    def locate(self) -> Optional[Path]:
        """Best-effort xppbp.exe discovery. Returns None when the binary isn't installed."""
        if self._explicit_path:
            p = Path(self._explicit_path)
            return p if p.is_file() else None

        from_path = shutil.which("xppbp.exe") or shutil.which("xppbp")
        if from_path:
            return Path(from_path)

        for raw in list(self._extra_search_paths) + list(_DEFAULT_SEARCH_PATHS):
            candidate = Path(raw) / "xppbp.exe"
            if candidate.is_file():
                return candidate
        return None

    def run(self, params: XppBpRunnerToolInputSchema) -> XppBpRunnerToolOutputSchema:
        exe = self.locate()
        if exe is None:
            return XppBpRunnerToolOutputSchema(
                tool_available=False,
                return_code=None,
                findings=[],
                log_xml_path=None,
                car_path=None,
                details=(
                    "xppbp.exe was not found on PATH or in any of the common D365 dev VM locations. "
                    "BP analysis requires a Windows machine with D365 F&O dev tooling installed. "
                    "On Linux/CI runners this is expected — branch on `tool_available` in the caller."
                ),
            )

        metadata = Path(params.metadata_path).expanduser().resolve()
        if not metadata.is_dir():
            return XppBpRunnerToolOutputSchema(
                tool_available=True,
                return_code=None,
                findings=[],
                log_xml_path=None,
                car_path=None,
                details=f"metadata_path is not a directory: {metadata}",
            )

        with tempfile.TemporaryDirectory(prefix="xppbp_") as tmp:
            tmp_dir = Path(tmp)
            log_xml = tmp_dir / "bp.xml"
            car_path = tmp_dir / "car.xlsx" if params.generate_car else None

            cmd = [
                str(exe),
                f"-metadata={metadata}",
                f"-model={params.model_name}",
                f"-xmlLog={log_xml}",
                "-all",
            ]
            if car_path is not None:
                cmd.append(f"-car={car_path}")
            cmd.extend(params.extra_args)

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=params.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return XppBpRunnerToolOutputSchema(
                    tool_available=True,
                    return_code=None,
                    findings=[],
                    log_xml_path=None,
                    car_path=None,
                    details=f"xppbp.exe timed out after {params.timeout_seconds}s",
                )

            findings = _parse_log(log_xml) if log_xml.is_file() else []
            return XppBpRunnerToolOutputSchema(
                tool_available=True,
                return_code=result.returncode,
                findings=findings,
                log_xml_path=str(log_xml) if log_xml.is_file() else None,
                car_path=str(car_path) if car_path and car_path.is_file() else None,
                details=(
                    f"xppbp.exe completed with exit code {result.returncode}; "
                    f"{len(findings)} finding(s) parsed."
                ),
            )


def _parse_log(xml_path: Path) -> List[BpFinding]:
    """Parse the xppbp XML log permissively. Accepts <Item>, <Diagnostic>, or <Issue> nodes."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    findings: List[BpFinding] = []
    for node in tree.iter():
        tag = node.tag.split("}", 1)[-1]
        if tag not in {"Item", "Diagnostic", "Issue", "Finding"}:
            continue
        attrs = {k.lower(): v for k, v in node.attrib.items()}
        rule = attrs.get("code") or attrs.get("rule") or attrs.get("id") or "unknown"
        severity = attrs.get("severity") or attrs.get("type") or ""
        file_attr = attrs.get("path") or attrs.get("file") or attrs.get("filepath")
        line_attr = attrs.get("line") or attrs.get("linenumber")
        line_number: Optional[int] = None
        if line_attr:
            try:
                line_number = int(line_attr)
            except ValueError:
                line_number = None
        message = (
            attrs.get("description")
            or attrs.get("message")
            or (node.text or "").strip()
            or rule
        )
        findings.append(
            BpFinding(
                rule=rule,
                severity=severity,
                file_path=file_attr,
                line_number=line_number,
                message=message,
            )
        )
    return findings


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    tool = XppBpRunnerTool()
    out = tool.run(
        XppBpRunnerToolInputSchema(
            metadata_path=os.environ.get("D365_METADATA_PATH", "."),
            model_name=os.environ.get("D365_MODEL_NAME", "ApplicationFoundation"),
        )
    )
    print(f"tool_available={out.tool_available}, return_code={out.return_code}")
    print(out.details)
    for f in out.findings[:10]:
        print(f"  [{f.severity}] {f.rule} {f.file_path}:{f.line_number}  {f.message[:120]}")
