---
name: xpp-authoring
description: Scaffold and wire X++ (Microsoft Dynamics 365 F&O / AX) AOT objects — classes, table extensions, form extensions, Chain of Command handlers, query objects, EDTs, base enums — following the modern extension model (not over-layering). Use when the user asks to "create an X++ class", "scaffold a table extension", "add a CoC handler", "build a SysOperation service", "wire up an X++ Args call", "add an event subscriber", or runs `/atomic-agents:xpp-authoring`.
---

# Author an X++ AOT Object

You are building inside a D365 F&O / AX X++ codebase. Every AOT object lives under a model, and modern customization is done via **extensions** — never over-layering. This skill is the action-oriented path: clarify → plan → write → verify.

For deep material (extension model rationale, CoC patterns, Common Table Expression idioms, security key wiring), the authority is the sibling reference files under `references/`. Open `references/aot-objects.md` first when unsure which object kind to use, `references/coc-patterns.md` before writing CoC, and `references/extension-vs-overlayering.md` if you're tempted to over-layer.

## When this fires vs the umbrella `framework` skill

- **This skill**: the user is creating or wiring a specific X++ AOT object — "add a table extension on CustTable", "build a SysOperation service that exports invoices", "subscribe to SalesTable's posted event".
- **`framework` skill** (atomic-agents umbrella): unrelated — that's the Python framework skill. This skill is independent of it.

## Phase 1 — Clarify

Before writing, confirm:

1. **Object kind.** Class / class augmentation / table extension / form extension / data-entity / query object / SysOperation service / batch job / EDT / base enum / view? If unclear, walk the user through `references/aot-objects.md`.
2. **Target.** Which standard object (or custom) is being extended? Confirm the exact AOT name. Use `D365MetadataLookupTool` (see `atomic-forge/tools/d365_metadata_lookup/`) to confirm spelling/category for system tables and classes.
3. **Model.** Which model owns the new artifact? Confirm `Descriptor/<Model>.xml` exists and lists the right reference models. New work goes in a **custom model** — never directly inside an OOB model.
4. **Naming.** Prefix every new artifact with the customer/project prefix (e.g. `Acme_`). Existing prefixes in the model should be reused.
5. **Compile context.** Is this a green-field repo or an active model on a dev VM? If green-field, you may not be able to run `xppbp` locally — note that and rely on review instead.

If any of the above is ambiguous, **ask before writing**. The cost of a wrong-kind scaffold is real.

## Phase 2 — Plan

Sketch the file set you'll produce. The shape depends on object kind:

| Kind | Files |
|---|---|
| Class augmentation (CoC) | `<Model>/<Prefix>_<Target>_Extension.xpp` (single class, augments `<Target>`) |
| Table extension | A `.axtableextension` metadata XML + matching `.xpp` for any new methods on the augmenter class |
| Form extension | A `.axformextension` XML + augmenting class with event handlers |
| New class | `<Model>/<Prefix>_<Name>.xpp` |
| EDT | `.axedt` XML |
| Base enum | `.axenum` XML |
| SysOperation service | Contract class + Service class + Controller class (3 files) |
| Query object | `.axquery` XML |

State which files you'll touch, what they'll contain, and where they live. Get confirmation if more than 3 files are involved.

## Phase 3 — Write

Use the modern templates below as starting points. Adjust naming and the augmented target. Do **NOT** introduce over-layered code.

### Class augmentation with Chain of Command

```xpp
[ExtensionOf(classStr(SalesTableType))]
final class Acme_SalesTableType_Extension
{
    public boolean checkUpdate()
    {
        boolean ret = next checkUpdate();
        if (ret && this.salesTable().CustAccount == "")
        {
            ret = checkFailed("Customer account is required.");
        }
        return ret;
    }
}
```

**Rules:**
- `[ExtensionOf(classStr(...))]` — `classStr` for classes, `formStr` for forms, `tableStr` for tables, `formDataSourceStr(FormName, DataSource)` for a form data source.
- The augmenter class must be `final` and have no body fields.
- Every CoC method must include `next <methodName>(args)` unless you're deliberately replacing the base implementation.
- Return type and parameters must match the augmented method exactly.

### Table extension augmenter (X++ side; metadata is XML)

```xpp
[ExtensionOf(tableStr(CustTable))]
final class Acme_CustTable_Extension
{
    public void initValue()
    {
        next initValue();
        this.Acme_DefaultRegion = Acme_RegionDefaults::find().DefaultRegionId;
    }
}
```

### Form data source event subscriber

```xpp
public class Acme_SalesTableForm_EventHandler
{
    [FormDataSourceEventHandler(formDataSourceStr(SalesTable, SalesTable), FormDataSourceEventType::Written)]
    public static void SalesTable_OnWritten(FormDataSource sender, FormDataSourceEventArgs e)
    {
        SalesTable rec = sender.cursor();
        Acme_SalesPostingService::enqueueIfReady(rec);
    }
}
```

### SysOperation service (preferred over RunBaseBatch for new batch jobs)

```xpp
// Contract — DataMemberAttribute on every parameter the controller will pack.
[DataContractAttribute]
public class Acme_InvoiceExportContract
{
    private TransDate fromDate;
    private TransDate toDate;

    [DataMemberAttribute("FromDate")]
    public TransDate parmFromDate(TransDate _v = fromDate)
    {
        fromDate = _v;
        return fromDate;
    }

    [DataMemberAttribute("ToDate")]
    public TransDate parmToDate(TransDate _v = toDate)
    {
        toDate = _v;
        return toDate;
    }
}

// Service — pure work.
public class Acme_InvoiceExportService extends SysOperationServiceBase
{
    public void run(Acme_InvoiceExportContract _contract)
    {
        // ... exporter implementation ...
    }
}

// Controller — entry point.
public class Acme_InvoiceExportController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        Acme_InvoiceExportController controller = new Acme_InvoiceExportController(
            classStr(Acme_InvoiceExportService),
            methodStr(Acme_InvoiceExportService, run),
            SysOperationExecutionMode::Synchronous);
        controller.startOperation();
    }
}
```

### Canonical imports / utilities

```xpp
using System;
using Microsoft.Dynamics.AX.Metadata.Service;
// X++ does not have a "from" import; reference types by their fully-qualified AOT path
// and trust the project file references for assembly resolution.
```

Do **NOT**:
- `import com.microsoft.dynamics.*` — that's Java/AX 2009 style and won't compile.
- Use `System.IO.File` directly from server-tier X++ — go through `Server`-side wrappers.
- Hardcode labels — use `@SYS123` references or new project labels.

## Phase 4 — Verify

1. **Read what you wrote.** Open every new file and re-read it top to bottom.
2. **Compile (if a dev VM is available).** `xppc.exe -metadata=<packages> -compilermetadata=<compiler> -refPath=<bin> -modelmodule=<YourModel>`. On Linux you can't compile X++ — skip this and rely on review.
3. **Run BP analysis.** Use the `XppBpRunnerTool` if available; if `tool_available=false`, note the limitation rather than skipping the review category entirely.
4. **Smoke test the path** (if possible). For a SysOperation service, invoke the controller from a temporary job. For a CoC method, trigger the augmented base method via the form/menu item that calls into it.
5. **Hand off.** Tell the user exactly which files were created, where, and what manual step (if any) is still needed (e.g. "wire up the menu item in `<Model>.axproj`").

## Anti-patterns

- Adding methods to the AOT object directly via over-layering — always use a CoC augmenter class instead.
- Defining a new EDT when an existing OOB EDT already exists for the concept (e.g. `ItemId`, `CustAccount`).
- Using `RunBaseBatch` for new operation jobs — prefer `SysOperation`.
- Returning early from a CoC method without calling `next` "because it's faster" — that breaks base behavior silently.
- Building a "framework" class that bundles unrelated helpers under one name — keep classes small and named for the thing they do.
- Catching `Exception::Error` and swallowing it — let it propagate so the Infolog reports the failure.

## References

- `references/aot-objects.md` — what each AOT object kind is for and when to pick it.
- `references/coc-patterns.md` — Chain of Command do/don't with annotated examples.
- `references/extension-vs-overlayering.md` — why the modern extension model exists and how to migrate over-layered code off it.
