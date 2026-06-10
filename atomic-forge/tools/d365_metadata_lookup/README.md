# D365 Metadata Lookup Tool

## Overview
Reference table for ~45 well-known **Microsoft Dynamics 365 Finance & Operations** AOT objects — tables (`CustTable`, `InventTable`, `SalesLine`, …), classes (`RunBaseBatch`, `SysOperation`, `Query`, `xRecord`, …), EDTs (`ItemId`, `CustAccount`, …), base enums (`NoYes`, `SalesStatus`, …), and frameworks (`SysExtensionAttribute`, `Workflow`, `DimensionAttribute`).

Returns category, one-paragraph description, key members (fields / methods / enum values), and Microsoft Learn URLs.

**Self-contained** — no network calls. Unknown objects return an MS Learn search URL the agent can hand off to a web-search tool. Designed to compose with `XppCodebaseScanTool`: scan finds an object reference → lookup explains what it is.

## Prerequisites and Dependencies
- Python 3.12 or later
- atomic-agents (See [here](/README.md) for installation instructions)
- pydantic

## Installation
1. Using the CLI tool that comes with Atomic Agents. Run `atomic` and select the tool.
2. Or copy/paste the `tool/` folder into your project.

## Input & Output Structure

### Input Schema
- `object_name` (str): AOT name. Case-insensitive; canonical case is preserved in the output.

### Output Schema
- `canonical_name` (str): The original AOT name as bundled (camel-case preserved).
- `category` (str): One of `table`, `class`, `edt`, `base_enum`, `framework`, `form`, `unknown`.
- `description` (str): One-paragraph explanation.
- `key_members` (list[str]): Notable fields / methods / enum values.
- `references` (list[str]): Microsoft Learn URLs.
- `found` (bool): True if the object was in the bundled table.

## Usage

```python
from tool.d365_metadata_lookup import (
    D365MetadataLookupTool,
    D365MetadataLookupToolInputSchema,
)

tool = D365MetadataLookupTool()
out = tool.run(D365MetadataLookupToolInputSchema(object_name="CustTable"))
print(out.description)
print("Common fields:", ", ".join(out.key_members[:5]))
```

## Adding custom / ISV objects

```python
from tool.d365_metadata_lookup import (
    D365MetadataLookupTool,
    D365MetadataLookupToolConfig,
    MetadataEntry,
)

config = D365MetadataLookupToolConfig(extra_lookup={
    "AcmeCustomTable": MetadataEntry(
        category="table",
        description="Acme's custom posting target table.",
        members=["AcmeId", "AcmePostingType"],
        references=["https://docs.acme.example/AcmeCustomTable"],
    ),
})
tool = D365MetadataLookupTool(config=config)
```

`extra_lookup` is merged on top of the bundled data — supply an entry for an already-known object to override it.

## Limits
- Coverage is finite and opinionated. Bundled table is curated, not exhaustive. For obscure or version-specific objects use Microsoft Learn search.
- Does NOT validate that the running D365 environment actually has these objects (versions / installed modules can vary).

## Contributing
Add new objects by editing `_BUNDLED` in `tool/d365_metadata_lookup.py`. Each entry needs a category, description, members list, and at least one Microsoft Learn URL.

## License
This project is licensed under the same license as the main Atomic Agents project.
