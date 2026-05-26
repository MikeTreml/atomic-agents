# File Search Tool

## Overview
The File Search Tool is a recursive filesystem search inside the Atomic Agents ecosystem. It locates files by filename glob and/or by a regular expression matched against file contents. Pure stdlib — no external dependencies beyond `atomic-agents` and `pydantic`.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic

## Installation
1. Using the CLI tool that comes with Atomic Agents. Simply run `atomic` and select the tool from the list. After doing so you will be asked for a target directory to download the tool into.
2. Or copy/paste the `tool/` folder into your project, provided you already have atomic-agents installed.

## Input & Output Structure

### Input Schema
- `root_path` (str): Directory to start the search from. Searched recursively.
- `name_pattern` (str, optional): Filename glob (fnmatch syntax, e.g. `*.py`, `config.*`). Matched against the leaf filename, not the full path.
- `content_pattern` (str, optional): Regular expression matched against file contents. Omit to do name-only search.
- `case_insensitive` (bool, default `false`): Apply to both name and content patterns.
- `max_results` (int, default 200): Cap on returned matches.
- `skip_hidden` (bool, default `true`): Skip dot-prefixed files and directories.

### Output Schema
- `matches` (list[FileMatch]): Each with `path`, `size_bytes`, optional `matched_line_number`, optional `matched_line` (truncated to 400 chars).
- `truncated` (bool): True when `max_results` was hit before the walk completed.

## Usage

```python
from tool.file_search import FileSearchTool, FileSearchToolInputSchema

tool = FileSearchTool()
result = tool.run(FileSearchToolInputSchema(
    root_path="./src",
    name_pattern="*.py",
    content_pattern=r"class\s+\w+Tool\(BaseTool",
    max_results=20,
))

for m in result.matches:
    print(f"{m.path}:{m.matched_line_number}: {m.matched_line}")
```

## Notes
- Files larger than `config.max_file_bytes` (10 MiB by default) are skipped during **content** scanning to avoid loading huge binaries or logs. Filename-only matches are unaffected.
- Glob is fnmatch-style, not full git-ignore syntax. Use `**` is not supported — search is already recursive, so `*.py` matches any `.py` anywhere under `root_path`.

## Contributing
Contributions are welcome — fork, branch, commit, PR.

## License
This project is licensed under the same license as the main Atomic Agents project.
