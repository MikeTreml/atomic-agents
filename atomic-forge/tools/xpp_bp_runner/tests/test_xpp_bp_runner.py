import os
import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tool.xpp_bp_runner import (  # noqa: E402
    XppBpRunnerTool,
    XppBpRunnerToolConfig,
    XppBpRunnerToolInputSchema,
    _parse_log,
)


def test_locate_returns_none_when_not_installed():
    tool = XppBpRunnerTool(
        config=XppBpRunnerToolConfig(xppbp_path="/definitely/not/here/xppbp.exe")
    )
    assert tool.locate() is None


def test_run_reports_unavailable_gracefully():
    tool = XppBpRunnerTool(
        config=XppBpRunnerToolConfig(xppbp_path="/definitely/not/here/xppbp.exe")
    )
    out = tool.run(
        XppBpRunnerToolInputSchema(metadata_path="/tmp", model_name="MyModel")
    )
    assert out.tool_available is False
    assert out.return_code is None
    assert out.findings == []
    assert "xppbp.exe was not found" in out.details


def test_explicit_path_is_honored_when_present(tmp_path: Path):
    fake_exe = tmp_path / "xppbp.exe"
    fake_exe.write_text("not actually executable")
    tool = XppBpRunnerTool(config=XppBpRunnerToolConfig(xppbp_path=str(fake_exe)))
    located = tool.locate()
    assert located is not None
    assert located.name == "xppbp.exe"


def test_parse_log_handles_canonical_shape(tmp_path: Path):
    xml = textwrap.dedent(
        """\
        <Diagnostics>
          <Items>
            <Item Severity="Warning" Code="BPCheckXyz" Path="C:\\src\\Foo.xpp" Line="42"
                  Description="Foo is not great." />
            <Item Severity="Error" Code="BPCheckAbc" Path="C:\\src\\Bar.xpp" Line="7"
                  Description="Bar must be built." />
          </Items>
        </Diagnostics>
        """
    )
    log = tmp_path / "bp.xml"
    log.write_text(xml)
    findings = _parse_log(log)
    assert len(findings) == 2
    assert findings[0].rule == "BPCheckXyz"
    assert findings[0].severity == "Warning"
    assert findings[0].line_number == 42
    assert findings[1].rule == "BPCheckAbc"
    assert findings[1].severity == "Error"
    assert findings[1].file_path.endswith("Bar.xpp")


def test_parse_log_handles_alternative_shape(tmp_path: Path):
    xml = textwrap.dedent(
        """\
        <Report>
          <Diagnostic id="BPHardcoded" type="Info" file="MyClass.xpp" lineNumber="11">
            Hardcoded magic value detected.
          </Diagnostic>
        </Report>
        """
    )
    log = tmp_path / "bp2.xml"
    log.write_text(xml)
    findings = _parse_log(log)
    assert len(findings) == 1
    assert findings[0].rule == "BPHardcoded"
    assert findings[0].severity == "Info"
    assert findings[0].line_number == 11
    assert "Hardcoded" in findings[0].message


def test_parse_log_tolerates_malformed_xml(tmp_path: Path):
    bad = tmp_path / "broken.xml"
    bad.write_text("<not valid xml")
    assert _parse_log(bad) == []


def test_invalid_metadata_path_reports_cleanly(tmp_path: Path):
    fake_exe = tmp_path / "xppbp.exe"
    fake_exe.write_text("stub")
    tool = XppBpRunnerTool(config=XppBpRunnerToolConfig(xppbp_path=str(fake_exe)))
    out = tool.run(
        XppBpRunnerToolInputSchema(
            metadata_path="/nonexistent/abc",
            model_name="X",
        )
    )
    # Tool was located, so tool_available is True; but the run is short-circuited.
    assert out.tool_available is True
    assert "metadata_path is not a directory" in out.details


if __name__ == "__main__":
    test_locate_returns_none_when_not_installed()
    test_run_reports_unavailable_gracefully()
    test_explicit_path_is_honored_when_present(Path(tempfile.mkdtemp()))
    test_parse_log_handles_canonical_shape(Path(tempfile.mkdtemp()))
    test_parse_log_handles_alternative_shape(Path(tempfile.mkdtemp()))
    test_parse_log_tolerates_malformed_xml(Path(tempfile.mkdtemp()))
    test_invalid_metadata_path_reports_cleanly(Path(tempfile.mkdtemp()))
    print("ok")
