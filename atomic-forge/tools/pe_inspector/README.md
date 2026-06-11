# PE Inspector Tool

## Overview
Static analysis tool for Portable Executable (PE) files — Windows `.exe`, `.dll`, `.sys`, `.ocx`. Reads headers, imports, exports, sections, and metadata **without executing the binary**. Useful as a first-pass for reverse engineering, malware triage, or figuring out what a DLL exposes.

Built on top of the [`pefile`](https://github.com/erocarrera/pefile) library.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic
- pefile (>= 2024.8.26)

## Installation
1. Using the CLI tool that comes with Atomic Agents. Run `atomic` and select the tool.
2. Or copy/paste the `tool/` folder into your project after `pip install pefile`.

## Input & Output Structure

### Input Schema
- `file_path` (str): Path to a PE file.
- `include_imports` (bool, default `true`): Include imported DLLs and functions.
- `include_exports` (bool, default `true`): Include exported function names.
- `include_sections` (bool, default `true`): Include section table.
- `max_imports_per_dll` (int, default 50): Cap per-DLL function list size.

### Output Schema
- `file_path`, `size_bytes`, `sha256` — file metadata
- `machine` (str): `x64`, `i386`, `arm64`, `arm`, etc.
- `is_dll` / `is_executable` (bool)
- `entry_point`, `image_base` (int)
- `timestamp` (int, may be `None`): PE header build timestamp
- `subsystem` (str): `WINDOWS_GUI`, `WINDOWS_CUI`, `NATIVE`, etc.
- `sections` (list[PESection]): name, virtual_size, virtual_address, raw_size, characteristics
- `imports` (list[PEImport]): each with `dll`, `functions`, `truncated`
- `exports` (list[str]): function names exported by the DLL

## Usage

```python
from tool.pe_inspector import PEInspectorTool, PEInspectorToolInputSchema

tool = PEInspectorTool()
result = tool.run(PEInspectorToolInputSchema(file_path="C:/Windows/System32/kernel32.dll"))

print(f"{result.machine}, DLL={result.is_dll}, exports={len(result.exports)}")
for imp in result.imports:
    print(f"  imports from {imp.dll}: {', '.join(imp.functions[:3])} ...")
```

## Chaining with other tools
The output schema is designed to chain naturally into a research agent. Pattern:

1. `FileSearchTool` finds candidate DLLs under a directory.
2. `PEInspectorTool` extracts each DLL's imports/exports.
3. `DllResearchTool` looks up what each imported system DLL provides.
4. An `AtomicAgent` summarizes "what does this software do, and what system APIs does it touch?"

## Safety
This tool only **reads** the file — it does not load it via the OS loader, run it, or modify it. Safe to point at unknown / hostile binaries for triage.

## Contributing
Contributions welcome — fork, branch, commit, PR.

## License
This project is licensed under the same license as the main Atomic Agents project.
