# X++ Best Practice Runner Tool

## Overview
Subprocess wrapper around Microsoft's `xppbp.exe` — the official X++ Best Practice analyzer shipped with D365 F&O dev tooling. Runs BP rules over a metadata folder + model, parses the produced XML log into structured findings (rule, severity, file, line, message), and optionally generates the Customization Analysis Report (CAR).

**Graceful degradation when `xppbp.exe` isn't installed.** Returns a structured output with `tool_available=false` instead of raising, so agent pipelines on Linux/CI runners can branch cleanly.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic
- **Optional (runtime, not install):** D365 F&O dev tooling on Windows providing `xppbp.exe`. Without it, the tool reports as unavailable.

## Installation
1. Using the CLI tool that comes with Atomic Agents. Run `atomic` and select the tool.
2. Or copy/paste the `tool/` folder into your project.

## Input & Output Structure

### Input Schema
- `metadata_path` (str): Path to the D365 packages/metadata folder.
- `model_name` (str): Name of the model to analyze.
- `generate_car` (bool, default `false`): Produce the CAR upgrade-readiness report alongside the XML log.
- `extra_args` (list[str]): Extra args appended to the xppbp.exe command line.
- `timeout_seconds` (int, default 600): Subprocess timeout. Bump for large models.

### Output Schema
- `tool_available` (bool): `false` when `xppbp.exe` is not found.
- `return_code` (int | null): Exit code from xppbp.exe.
- `findings` (list[BpFinding]): Each with `rule`, `severity`, optional `file_path`, optional `line_number`, `message`.
- `log_xml_path` (str | null): Path to the raw XML log, for follow-up inspection.
- `car_path` (str | null): Path to the CAR report, when generated.
- `details` (str): Human-readable summary or error description.

## Discovery rules

The tool finds `xppbp.exe` in this order:
1. `config.xppbp_path` (explicit override).
2. `PATH` (via `shutil.which`).
3. `config.extra_search_paths`.
4. Built-in defaults: `C:\packages\bin`, `C:\AOSService\PackagesLocalDirectory\bin`, `K:\AosService\PackagesLocalDirectory\bin`, `J:\AosService\PackagesLocalDirectory\bin`.

## Usage

```python
from tool.xpp_bp_runner import XppBpRunnerTool, XppBpRunnerToolInputSchema

tool = XppBpRunnerTool()
out = tool.run(XppBpRunnerToolInputSchema(
    metadata_path=r"K:\AosService\PackagesLocalDirectory",
    model_name="MyExtensionModel",
    generate_car=True,
))

if not out.tool_available:
    print("Skipping BP analysis:", out.details)
else:
    for f in out.findings:
        print(f"[{f.severity}] {f.rule} {f.file_path}:{f.line_number}  {f.message}")
    if out.car_path:
        print("CAR report at", out.car_path)
```

## Limits
- The XML log shape across xppbp versions varies. The parser accepts the canonical `<Item>` shape and a few alternatives (`<Diagnostic>`, `<Issue>`, `<Finding>`) with permissive attribute lookup. If your version produces a different shape, fall back to inspecting `log_xml_path`.
- This tool does NOT perform BP analysis itself; it shells out to Microsoft's tool. Without `xppbp.exe` installed, the tool reports `tool_available=False`.

## Chaining

Pairs naturally with `XppCodebaseScanTool` (locate the model's source) and `D365MetadataLookupTool` (explain referenced AOT objects in the findings):

```
XppCodebaseScan  →  XppBpRunner  →  D365MetadataLookup
(find model src)    (run BP rules)   (explain referenced objects)
```

## Contributing
Add new XML shapes the parser should accept by extending `_parse_log()` in `tool/xpp_bp_runner.py` and adding a test fixture.

## License
This project is licensed under the same license as the main Atomic Agents project.
