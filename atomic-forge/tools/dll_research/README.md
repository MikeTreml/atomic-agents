# DLL Research Tool

## Overview
The DLL Research Tool answers "what does this Windows DLL do?" using a bundled, curated reference table covering ~30 of the most-imported Windows system DLLs (kernel32, user32, ntdll, ws2_32, crypt32, ...) plus the common C/C++ and .NET runtimes. Unknown DLLs return a Microsoft Learn search URL the agent can hand off to a web-search tool.

Self-contained — no network calls. Designed to chain with `PEInspectorTool`: extract imports → research each imported DLL.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic

## Installation
1. Using the CLI tool that comes with Atomic Agents. Run `atomic` and select the tool.
2. Or copy/paste the `tool/` folder into your project.

## Input & Output Structure

### Input Schema
- `dll_name` (str): Name of the DLL. Case-insensitive; the `.dll` suffix is optional.

### Output Schema
- `canonical_name` (str): Lowercase filename with `.dll` suffix.
- `category` (str): One of `windows-core`, `windows-gui`, `windows-net`, `crt`, `dotnet`, `unknown`.
- `description` (str): One-paragraph explanation.
- `common_functions` (list[str]): Notable exported functions (illustrative, not exhaustive).
- `references` (list[str]): URLs for deeper reading.
- `found` (bool): True if the DLL was in the bundled table.

## Usage

```python
from tool.dll_research import DllResearchTool, DllResearchToolInputSchema

tool = DllResearchTool()
out = tool.run(DllResearchToolInputSchema(dll_name="kernel32"))
print(out.description)
print("Examples:", ", ".join(out.common_functions[:5]))
```

## Adding custom DLLs

```python
from tool.dll_research import DllResearchTool, DllResearchToolConfig
from tool.dll_research import DllEntry

config = DllResearchToolConfig(extra_lookup={
    "MyAppCore.dll": DllEntry(
        category="unknown",
        description="My app's internal helper DLL.",
        functions=["MyAppInit", "MyAppShutdown"],
        references=["https://docs.example.com/myappcore"],
    ),
})
tool = DllResearchTool(config=config)
```

`extra_lookup` is merged on top of the bundled data — pass an entry for an already-known DLL to override it.

## Limits
- Coverage is finite. Bundled table is curated, not exhaustive. For unknown DLLs the tool returns a search URL rather than fabricating an answer.
- This tool does NOT verify that a DLL actually exports the functions listed under `common_functions`. To check what a specific binary actually exposes, pair with `PEInspectorTool`.

## Contributing
Add new DLLs by editing `_BUNDLED` in `tool/dll_research.py`. Each entry needs a category, description, function list, and reference URLs.

## License
This project is licensed under the same license as the main Atomic Agents project.
