# X++ Codebase Scan Tool

## Overview
Regex-based scan of a Microsoft Dynamics 365 F&O / AX **X++** codebase. Extracts declarations — classes, table extensions, methods, EDTs, base enums — and reports their file paths and line numbers.

**No D365 install or X++ compiler required.** Pure stdlib, so the tool runs in CI on Linux runners and on developer laptops without a dev VM. Best used as a first pass before pointing an agent at heavier tooling like Microsoft's `xppbp.exe` or a dedicated X++ MCP server.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic

## Installation
1. Using the CLI tool that comes with Atomic Agents. Run `atomic` and select the tool.
2. Or copy/paste the `tool/` folder into your project.

## Input & Output Structure

### Input Schema
- `root_path` (str): Directory to start the scan from. Searched recursively.
- `kinds` (list[str], default all): Subset of `class`, `method`, `table_extension`, `edt`, `base_enum`.
- `file_pattern` (str, default `*.xpp`): Filename glob.
- `max_results` (int, default 500): Cap on declarations returned.
- `skip_hidden` (bool, default `true`): Skip dot-prefixed files and directories.

### Output Schema
- `declarations` (list[XppDeclaration]): Each with `kind`, `name`, optional `extends`, optional `parent` class (for methods), `file_path`, `line_number`, `signature` (raw matched line, truncated to 400 chars).
- `files_scanned` (int): Number of files actually opened during the scan.
- `truncated` (bool): True when `max_results` was hit before the walk completed.

## Usage

```python
from tool.xpp_codebase_scan import XppCodebaseScanTool, XppCodebaseScanToolInputSchema

tool = XppCodebaseScanTool()
result = tool.run(XppCodebaseScanToolInputSchema(
    root_path="./MyModel",
    kinds=["class", "table_extension", "method"],
))

for d in result.declarations:
    print(f"{d.kind:<15} {d.name}  @ {d.file_path}:{d.line_number}")
```

## Limits
- Regex-based, not parser-based. False positives are possible on heavily formatted or generated source. For authoritative analysis use Microsoft's X++ compiler via `xpp_bp_runner` or an X++ MCP server.
- Method-to-class attribution is lexical (the nearest preceding `class X` line), not scope-aware. Nested or interface-only methods may be misattributed.
- Doesn't follow `#include` / partial-class composition. Each file is scanned independently.

## Chaining

Natural pipeline:

```
XppCodebaseScanTool   →   D365MetadataLookupTool   →   XppBpRunnerTool
(find classes/methods)    (explain referenced objects)   (run BP rules)
```

## Contributing
Contributions welcome — fork, branch, commit, PR. New regex anchors should ship with a unit test in `tests/test_xpp_codebase_scan.py`.

## License
This project is licensed under the same license as the main Atomic Agents project.
