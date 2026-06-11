import fnmatch
import os
import re
from pathlib import Path
from typing import List, Optional

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class FileSearchToolInputSchema(BaseIOSchema):
    """
    Tool for searching files under a directory by filename glob and/or
    by a regular expression matched against file contents. Use this to
    locate code, configuration, or log files without leaving the agent
    pipeline. Returns paths plus, when content search is used, the first
    matching line in each file.
    """

    root_path: str = Field(..., description="Directory to start the search from. Searched recursively.")
    name_pattern: Optional[str] = Field(
        default=None,
        description="Filename glob (fnmatch syntax, e.g. '*.py', 'config.*'). Matched against the leaf filename, not the full path.",
    )
    content_pattern: Optional[str] = Field(
        default=None,
        description="Regular expression to match against file contents. If omitted, only filename matching is used.",
    )
    case_insensitive: bool = Field(
        default=False, description="Apply case-insensitive matching to both name and content patterns."
    )
    max_results: int = Field(default=200, description="Cap on number of file matches returned.", ge=1)
    skip_hidden: bool = Field(
        default=True, description="Skip dot-prefixed files and directories (e.g. .git, .venv)."
    )


#################
# OUTPUT SCHEMA #
#################
class FileMatch(BaseIOSchema):
    """A single file that matched the search criteria."""

    path: str = Field(..., description="Absolute path to the file.")
    size_bytes: int = Field(..., description="File size in bytes.")
    matched_line_number: Optional[int] = Field(
        default=None, description="1-based line number of the first content match, if a content_pattern was used."
    )
    matched_line: Optional[str] = Field(
        default=None, description="The first line whose content matched the regex (truncated to 400 chars), if any."
    )


class FileSearchToolOutputSchema(BaseIOSchema):
    """Schema for the output of the FileSearchTool."""

    matches: List[FileMatch] = Field(default_factory=list, description="Files that matched.")
    truncated: bool = Field(
        default=False, description="True when the result set was capped by max_results before the walk completed."
    )


#################
# CONFIGURATION #
#################
class FileSearchToolConfig(BaseToolConfig):
    """
    Configuration for the FileSearchTool.

    Attributes:
        max_file_bytes: Files larger than this are skipped during content scanning to avoid loading
            binaries or huge logs into memory. Filename-only matches are unaffected.
    """

    max_file_bytes: int = 10 * 1024 * 1024  # 10 MiB


#####################
# MAIN TOOL & LOGIC #
#####################
class FileSearchTool(BaseTool[FileSearchToolInputSchema, FileSearchToolOutputSchema]):
    """Recursive filesystem search by name pattern and/or content regex."""

    def __init__(self, config: FileSearchToolConfig = FileSearchToolConfig()):
        super().__init__(config)
        self.max_file_bytes = config.max_file_bytes

    def run(self, params: FileSearchToolInputSchema) -> FileSearchToolOutputSchema:
        root = Path(params.root_path).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"root_path is not a directory: {root}")

        flags = re.IGNORECASE if params.case_insensitive else 0
        content_re = re.compile(params.content_pattern, flags) if params.content_pattern else None

        matches: List[FileMatch] = []
        truncated = False

        for dirpath, dirnames, filenames in os.walk(root):
            if params.skip_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                filenames = [f for f in filenames if not f.startswith(".")]

            for fname in filenames:
                if params.name_pattern and not self._name_match(fname, params.name_pattern, params.case_insensitive):
                    continue

                full = Path(dirpath) / fname
                try:
                    size = full.stat().st_size
                except OSError:
                    continue

                line_no: Optional[int] = None
                line_text: Optional[str] = None

                if content_re is not None:
                    if size > self.max_file_bytes:
                        continue
                    line_no, line_text = self._first_match(full, content_re)
                    if line_no is None:
                        continue

                matches.append(
                    FileMatch(
                        path=str(full),
                        size_bytes=size,
                        matched_line_number=line_no,
                        matched_line=line_text,
                    )
                )
                if len(matches) >= params.max_results:
                    truncated = True
                    return FileSearchToolOutputSchema(matches=matches, truncated=truncated)

        return FileSearchToolOutputSchema(matches=matches, truncated=truncated)

    @staticmethod
    def _name_match(fname: str, pattern: str, case_insensitive: bool) -> bool:
        if case_insensitive:
            return fnmatch.fnmatch(fname.lower(), pattern.lower())
        return fnmatch.fnmatchcase(fname, pattern)

    @staticmethod
    def _first_match(path: Path, regex: re.Pattern) -> tuple[Optional[int], Optional[str]]:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, start=1):
                    if regex.search(line):
                        return i, line.rstrip("\n")[:400]
        except OSError:
            pass
        return None, None


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    tool = FileSearchTool()
    result = tool.run(
        FileSearchToolInputSchema(
            root_path=".",
            name_pattern="*.py",
            content_pattern=r"class\s+\w+Tool\(BaseTool",
            max_results=5,
        )
    )
    for m in result.matches:
        print(f"{m.path}:{m.matched_line_number}: {m.matched_line}")
    if result.truncated:
        print("(results truncated)")
