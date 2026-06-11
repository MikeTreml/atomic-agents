import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tool.file_search import (  # noqa: E402
    FileSearchTool,
    FileSearchToolConfig,
    FileSearchToolInputSchema,
)


def _make_tree(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "alpha.py").write_text("import os\n# TODO: refactor\nclass Foo: ...\n")
    (root / "src" / "beta.py").write_text("# nothing interesting here\n")
    (root / "src" / "README.md").write_text("# Project\n")
    (root / ".hidden").mkdir()
    (root / ".hidden" / "alpha.py").write_text("class Hidden: ...\n")
    (root / "logs").mkdir()
    (root / "logs" / "app.log").write_text("error: boom\nok\n")


def test_name_pattern_only():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp))
        tool = FileSearchTool()
        result = tool.run(FileSearchToolInputSchema(root_path=tmp, name_pattern="*.py"))
        names = sorted(Path(m.path).name for m in result.matches)
        assert names == ["alpha.py", "beta.py"]  # .hidden/alpha.py excluded by skip_hidden
        assert result.truncated is False


def test_content_pattern_filters_files():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp))
        tool = FileSearchTool()
        result = tool.run(
            FileSearchToolInputSchema(
                root_path=tmp, name_pattern="*.py", content_pattern=r"TODO"
            )
        )
        assert len(result.matches) == 1
        assert Path(result.matches[0].path).name == "alpha.py"
        assert result.matches[0].matched_line_number == 2
        assert "TODO" in result.matches[0].matched_line


def test_case_insensitive():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp))
        tool = FileSearchTool()
        result = tool.run(
            FileSearchToolInputSchema(
                root_path=tmp, name_pattern="*.PY", case_insensitive=True
            )
        )
        assert {Path(m.path).name for m in result.matches} == {"alpha.py", "beta.py"}


def test_max_results_truncates():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp))
        tool = FileSearchTool()
        result = tool.run(
            FileSearchToolInputSchema(root_path=tmp, name_pattern="*", max_results=1)
        )
        assert len(result.matches) == 1
        assert result.truncated is True


def test_skip_hidden_false_includes_dotfiles():
    with tempfile.TemporaryDirectory() as tmp:
        _make_tree(Path(tmp))
        tool = FileSearchTool()
        result = tool.run(
            FileSearchToolInputSchema(root_path=tmp, name_pattern="*.py", skip_hidden=False)
        )
        names = sorted(Path(m.path).name for m in result.matches)
        assert names == ["alpha.py", "alpha.py", "beta.py"]


def test_invalid_root_raises():
    tool = FileSearchTool()
    try:
        tool.run(FileSearchToolInputSchema(root_path="/nonexistent/abc"))
    except ValueError:
        return
    raise AssertionError("expected ValueError for missing root_path")


def test_large_file_skipped_for_content_scan():
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "big.txt").write_text("needle\n" + "x" * 200)
        tool = FileSearchTool(config=FileSearchToolConfig(max_file_bytes=10))
        result = tool.run(
            FileSearchToolInputSchema(
                root_path=tmp, name_pattern="*.txt", content_pattern=r"needle"
            )
        )
        assert result.matches == []


if __name__ == "__main__":
    test_name_pattern_only()
    test_content_pattern_filters_files()
    test_case_insensitive()
    test_max_results_truncates()
    test_skip_hidden_false_includes_dotfiles()
    test_invalid_root_raises()
    test_large_file_skipped_for_content_scan()
    print("ok")
