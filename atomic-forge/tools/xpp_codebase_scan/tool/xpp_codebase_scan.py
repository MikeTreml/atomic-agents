import os
import re
from pathlib import Path
from typing import List, Optional, Set

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class XppCodebaseScanToolInputSchema(BaseIOSchema):
    """
    Tool for scanning a Microsoft Dynamics 365 F&O / AX X++ codebase by regex
    to extract declarations: classes, table extensions, methods, EDTs declared
    inline, and base enums. Pure stdlib — no D365 install or X++ compiler
    required, so it works in CI on Linux runners and on developer laptops
    without a dev VM. Use as a first pass before pointing an agent at heavier
    tooling like xppbp or an MCP server.
    """

    root_path: str = Field(..., description="Directory to start the scan from. Searched recursively.")
    kinds: List[str] = Field(
        default_factory=lambda: ["class", "method", "table_extension", "edt", "base_enum"],
        description=(
            "Which declaration kinds to collect. Any of: 'class', 'method', "
            "'table_extension', 'edt', 'base_enum'."
        ),
    )
    file_pattern: str = Field(
        default="*.xpp", description="Filename glob (fnmatch syntax) used to gate which files are read."
    )
    max_results: int = Field(default=500, ge=1, description="Cap on number of declarations returned.")
    skip_hidden: bool = Field(default=True, description="Skip dot-prefixed files and directories.")


#################
# OUTPUT SCHEMA #
#################
class XppDeclaration(BaseIOSchema):
    """A single declaration extracted from an X++ source file."""

    kind: str = Field(..., description="One of: 'class', 'method', 'table_extension', 'edt', 'base_enum'.")
    name: str = Field(..., description="Declared identifier.")
    extends: Optional[str] = Field(
        default=None, description="Base type for class / table_extension declarations, if visible."
    )
    parent: Optional[str] = Field(
        default=None, description="For methods: the enclosing class name (best-effort, based on lexical order)."
    )
    file_path: str = Field(..., description="Absolute path to the source file.")
    line_number: int = Field(..., description="1-based line number of the declaration.")
    signature: str = Field(..., description="Raw matched line text (truncated to 400 chars).")


class XppCodebaseScanToolOutputSchema(BaseIOSchema):
    """Schema for the output of the XppCodebaseScanTool."""

    declarations: List[XppDeclaration] = Field(default_factory=list, description="Declarations found.")
    files_scanned: int = Field(..., description="Number of .xpp files actually opened during the scan.")
    truncated: bool = Field(
        default=False, description="True when max_results was hit before the walk completed."
    )


#################
# CONFIGURATION #
#################
class XppCodebaseScanToolConfig(BaseToolConfig):
    """
    Configuration for the XppCodebaseScanTool.

    Attributes:
        max_file_bytes: Files larger than this are skipped to keep scans bounded. X++ source files
            are typically small (a few KB to ~100 KB); anything multi-MB is likely generated noise.
    """

    max_file_bytes: int = 2 * 1024 * 1024  # 2 MiB


# Regex anchors. X++ classes look much like C#/Java:
#   public class FooBar extends Common implements MyInterface
# Table extensions follow the modern extension model. EDTs and BaseEnums can
# appear as class-form declarations in modernized projects.
_RE_CLASS = re.compile(
    r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+|abstract\s+|final\s+)*"
    r"class\s+(?P<name>\w+)"
    r"(?:\s+extends\s+(?P<extends>\w+))?",
    re.IGNORECASE,
)
_RE_TABLE_EXTENSION = re.compile(
    r"^\s*(?:public\s+|internal\s+|final\s+)*"
    r"(?:final\s+)?class\s+(?P<name>\w+)_Extension\b"
    r"(?:\s+extends\s+(?P<extends>\w+))?",
    re.IGNORECASE,
)
_RE_EDT = re.compile(
    r"^\s*(?:public\s+|internal\s+)*"
    r"(?:edt|extended\s+data\s+type)\s+(?P<name>\w+)",
    re.IGNORECASE,
)
_RE_BASE_ENUM = re.compile(
    r"^\s*(?:public\s+|internal\s+)*"
    r"(?:enum|baseenum|base\s+enum)\s+(?P<name>\w+)",
    re.IGNORECASE,
)
# Methods inside a class body. Type can be a single identifier (str, int, void, MyClass)
# or generic-shaped (List<Foo>). We require an opening paren so we don't catch field
# declarations.
_RE_METHOD = re.compile(
    r"^\s*(?:public\s+|private\s+|protected\s+|internal\s+|static\s+|abstract\s+|final\s+|server\s+|client\s+)*"
    r"(?P<return_type>[\w<>,\s]+?)\s+"
    r"(?P<name>\w+)\s*\([^;]*\)\s*$",
)
_RE_CLASS_OPEN = re.compile(r"^\s*[^/]*\bclass\s+(?P<name>\w+)")


#####################
# MAIN TOOL & LOGIC #
#####################
class XppCodebaseScanTool(BaseTool[XppCodebaseScanToolInputSchema, XppCodebaseScanToolOutputSchema]):
    """Regex-based scan of an X++ codebase for declaration nodes."""

    _VALID_KINDS: Set[str] = {"class", "method", "table_extension", "edt", "base_enum"}

    def __init__(self, config: XppCodebaseScanToolConfig = XppCodebaseScanToolConfig()):
        super().__init__(config)
        self.max_file_bytes = config.max_file_bytes

    def run(self, params: XppCodebaseScanToolInputSchema) -> XppCodebaseScanToolOutputSchema:
        root = Path(params.root_path).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"root_path is not a directory: {root}")

        kinds = {k.lower() for k in params.kinds}
        unknown = kinds - self._VALID_KINDS
        if unknown:
            raise ValueError(f"unknown kinds: {sorted(unknown)}; valid: {sorted(self._VALID_KINDS)}")

        declarations: List[XppDeclaration] = []
        files_scanned = 0
        truncated = False

        for dirpath, dirnames, filenames in os.walk(root):
            if params.skip_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                filenames = [f for f in filenames if not f.startswith(".")]

            for fname in filenames:
                if not _fnmatch_lower(fname, params.file_pattern):
                    continue
                full = Path(dirpath) / fname
                try:
                    if full.stat().st_size > self.max_file_bytes:
                        continue
                except OSError:
                    continue

                files_scanned += 1
                if self._scan_file(full, kinds, declarations, params.max_results):
                    truncated = True
                    return XppCodebaseScanToolOutputSchema(
                        declarations=declarations, files_scanned=files_scanned, truncated=True
                    )

        return XppCodebaseScanToolOutputSchema(
            declarations=declarations, files_scanned=files_scanned, truncated=truncated
        )

    def _scan_file(
        self,
        path: Path,
        kinds: Set[str],
        out: List[XppDeclaration],
        max_results: int,
    ) -> bool:
        """Return True when max_results has been hit."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False

        current_class: Optional[str] = None
        for i, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.rstrip()

            # Track the lexically nearest enclosing class for method `parent` attribution.
            cm = _RE_CLASS_OPEN.match(line)
            if cm:
                current_class = cm.group("name")

            for kind, regex in (
                ("table_extension", _RE_TABLE_EXTENSION),  # check before generic class
                ("class", _RE_CLASS),
                ("edt", _RE_EDT),
                ("base_enum", _RE_BASE_ENUM),
                ("method", _RE_METHOD),
            ):
                if kind not in kinds:
                    continue
                m = regex.match(line)
                if not m:
                    continue
                # Skip methods that don't sit inside a known class — those are usually
                # false positives from class/EDT/enum lines that already matched above.
                if kind == "method":
                    if current_class is None:
                        continue
                    if m.group("name") in {"class", "extends", "implements"}:
                        continue
                out.append(
                    XppDeclaration(
                        kind=kind,
                        name=m.group("name"),
                        extends=m.groupdict().get("extends"),
                        parent=current_class if kind == "method" else None,
                        file_path=str(path),
                        line_number=i,
                        signature=line[:400],
                    )
                )
                if len(out) >= max_results:
                    return True
                break  # one kind per line is enough
        return False


def _fnmatch_lower(name: str, pattern: str) -> bool:
    import fnmatch

    return fnmatch.fnmatch(name.lower(), pattern.lower())


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    import sys

    tool = XppCodebaseScanTool()
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    out = tool.run(
        XppCodebaseScanToolInputSchema(
            root_path=target,
            kinds=["class", "table_extension", "method"],
            max_results=50,
        )
    )
    print(f"scanned {out.files_scanned} file(s); found {len(out.declarations)} declaration(s)")
    for d in out.declarations[:25]:
        suffix = f" extends {d.extends}" if d.extends else ""
        parent = f"  ({d.parent})" if d.parent else ""
        print(f"  {d.kind:<15} {d.name}{suffix}  @ {d.file_path}:{d.line_number}{parent}")
