import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tool.xpp_codebase_scan import (  # noqa: E402
    XppCodebaseScanTool,
    XppCodebaseScanToolConfig,
    XppCodebaseScanToolInputSchema,
)


_SAMPLE_CLASS = """\
public class CustTable_Extension extends CustTable
{
    public void initValue()
    {
        next initValue();
    }

    private str customerGreeting(str name)
    {
        return strFmt("Hello %1", name);
    }
}
"""

_SAMPLE_FORM_CLASS = """\
[ExtensionOf(formStr(SalesTable))]
final class SalesTable_DemoExt_Extension
{
    public void init()
    {
        next init();
    }
}
"""

_SAMPLE_OBJ = """\
public class MyService extends RunBaseBatch
{
    public boolean run()
    {
        return true;
    }
}
"""


def _make_xpp_tree(root: Path) -> None:
    (root / "Cust").mkdir()
    (root / "Cust" / "CustTable_Extension.xpp").write_text(_SAMPLE_CLASS)
    (root / "Sales").mkdir()
    (root / "Sales" / "SalesTable_DemoExt_Extension.xpp").write_text(_SAMPLE_FORM_CLASS)
    (root / "MyService.xpp").write_text(_SAMPLE_OBJ)
    (root / "README.md").write_text("# not an xpp file\n")


def test_classes_are_extracted():
    with tempfile.TemporaryDirectory() as tmp:
        _make_xpp_tree(Path(tmp))
        tool = XppCodebaseScanTool()
        out = tool.run(
            XppCodebaseScanToolInputSchema(root_path=tmp, kinds=["class", "table_extension"])
        )
        names = {(d.kind, d.name) for d in out.declarations}
        assert ("table_extension", "CustTable") in names
        assert ("table_extension", "SalesTable_DemoExt") in names
        assert ("class", "MyService") in names
        assert out.files_scanned == 3  # README.md excluded by *.xpp filter


def test_methods_attribute_to_enclosing_class():
    with tempfile.TemporaryDirectory() as tmp:
        _make_xpp_tree(Path(tmp))
        tool = XppCodebaseScanTool()
        out = tool.run(XppCodebaseScanToolInputSchema(root_path=tmp, kinds=["method"]))
        methods = [(d.name, d.parent) for d in out.declarations]
        assert ("initValue", "CustTable_Extension") in methods
        assert ("customerGreeting", "CustTable_Extension") in methods
        assert ("init", "SalesTable_DemoExt_Extension") in methods
        assert ("run", "MyService") in methods


def test_unknown_kind_raises():
    with tempfile.TemporaryDirectory() as tmp:
        tool = XppCodebaseScanTool()
        try:
            tool.run(
                XppCodebaseScanToolInputSchema(root_path=tmp, kinds=["not_a_real_kind"])
            )
        except ValueError as e:
            assert "unknown kinds" in str(e)
            return
        raise AssertionError("expected ValueError for unknown kind")


def test_missing_root_raises():
    tool = XppCodebaseScanTool()
    try:
        tool.run(XppCodebaseScanToolInputSchema(root_path="/nonexistent/abc"))
    except ValueError:
        return
    raise AssertionError("expected ValueError for missing root")


def test_max_results_truncates():
    with tempfile.TemporaryDirectory() as tmp:
        _make_xpp_tree(Path(tmp))
        tool = XppCodebaseScanTool()
        out = tool.run(
            XppCodebaseScanToolInputSchema(root_path=tmp, kinds=["class", "method"], max_results=1)
        )
        assert len(out.declarations) == 1
        assert out.truncated is True


def test_large_file_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        big = Path(tmp) / "Big.xpp"
        big.write_text(_SAMPLE_CLASS + "\n" + "x" * (3 * 1024 * 1024))
        tool = XppCodebaseScanTool(config=XppCodebaseScanToolConfig(max_file_bytes=1024))
        out = tool.run(XppCodebaseScanToolInputSchema(root_path=tmp, kinds=["class"]))
        assert out.files_scanned == 0
        assert out.declarations == []


if __name__ == "__main__":
    test_classes_are_extracted()
    test_methods_attribute_to_enclosing_class()
    test_unknown_kind_raises()
    test_missing_root_raises()
    test_max_results_truncates()
    test_large_file_skipped()
    print("ok")
