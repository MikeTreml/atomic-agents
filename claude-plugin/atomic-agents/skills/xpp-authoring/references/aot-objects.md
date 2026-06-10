# AOT Object Reference

Quick orientation: when scaffolding new D365 F&O X++ code, the first question is **which AOT object kind**. Pick the wrong kind and you ship something that compiles but doesn't extend cleanly. The shorter the section, the safer the default.

## Tables

- **Use a new table** when you're storing a new entity (rows of master or transactional data) that doesn't fit any existing one.
- **Use a table extension** (`.axtableextension`) to add fields, indexes, or relations to an existing OOB table. This is the default for "we need to track one more attribute on customers / sales orders / etc."

Methods on the augmenter class use `[ExtensionOf(tableStr(Target))]` + `final class Prefix_Target_Extension`. CoC method names match the target's method names.

## Forms

- **Form extension** (`.axformextension`) for adding controls, data sources, or behavior to an existing form. Augmenter class hosts event handlers + CoC.
- **New form** only when the use case has no existing form (rare). Prefer extending list pages over creating new ones.

## Classes

- **Class augmentation (CoC)** to change behavior of an existing class without over-layering. Augmenter is `final class Prefix_Target_Extension` with `[ExtensionOf(classStr(Target))]`.
- **New class** for new behavior. Prefix it with your project prefix. Mark as `final` unless you have a concrete reason to allow subclassing.

## EDTs (Extended Data Types)

EDTs are typed wrappers around primitives (`str`, `int`, `date`) plus optional relations to tables. Use one when:
- You want consistent display, label, and length across many fields representing the same concept.
- You want a relation back to a master table so look-up controls "just work".

If an OOB EDT already exists for the concept (`ItemId`, `CustAccount`, `LedgerAccount`, `TransDate`, `NoYesId`, ...), **use it instead of creating a duplicate**. Check via `D365MetadataLookupTool`.

## Base enums

Base enums = closed sets of named integer values surfaced as types. Create one when you have a small (≤ ~10) fixed list that other code will branch on. Don't use base enums for ranges that change frequently or are large — use a master table instead.

If an OOB enum fits (`NoYes`, `SalesStatus`, `PurchStatus`, `Module`, `Gender`, ...), reuse it.

## Queries

X++ queries are reusable, declarative `select` graphs. Create a `.axquery` when:
- The same data shape will be consumed by a SysOperation, an SSRS report, AND a Data Entity.
- The query is large enough that inlining it as code would be opaque.

Otherwise build the query inline using `Query`, `QueryBuildDataSource`, `QueryRun`.

## Data Entities (`.axentity`)

Wire integration surface for OData and Data Management. Create a Data Entity when external systems need to read or write your data. Don't create one as the primary write path for in-app forms — use a table directly.

## SysOperation services

The modern batch / operation framework. Three files: a `[DataContractAttribute]` contract class, a service class extending `SysOperationServiceBase`, a controller class extending `SysOperationServiceController`.

Prefer this for **anything you want runnable in batch**. The legacy `RunBaseBatch` family still works but is more brittle around extension and serialization.

## RunBaseBatch / RunBase

Acceptable for **one-off ad-hoc jobs** (a developer running cleanup once). For anything that will be exposed to users or run on a schedule, use SysOperation instead.

## Workflows

Use the Workflow framework when you need approval/rejection routing with audit. The framework wires up a workflow type, configurations, providers, and a WorkflowDocument over your record. This is more setup than X++ alone — consult `references/coc-patterns.md` only if you're adding CoC into an existing workflow.

## Event subscribers (decorated handler methods)

Use when:
- You don't need to wrap the base behavior — you just need to **react** to it after it happens.
- The target exposes a Pre/Post event for the moment you care about.
- You'd otherwise create a CoC handler that only contains the line `next foo(); doExtra();`.

Standard attributes:
- `[FormDataSourceEventHandler(formDataSourceStr(F, DS), FormDataSourceEventType::Written)]`
- `[FormControlEventHandler(formControlStr(F, Btn), FormControlEventType::Clicked)]`
- `[DataEventHandler(tableStr(T), DataEventType::Inserted)]`

Subscriber methods are `public static void` with the standard `(<Sender>, <Args>)` signature.

## Quick-pick cheat sheet

| You want to… | Use |
|---|---|
| Add a field to CustTable | Table extension on `CustTable` |
| Validate a sales order header before save | CoC on `SalesTableType.checkUpdate()` (or PreEvent on the form data source `Written`) |
| Run an exporter on a schedule | SysOperation service |
| Add a new master entity | New table + new form + (optional) new data entity |
| Add a button to the customer form | Form extension + `FormControlEventHandler` |
| React to "sales order posted" | Event handler — find the post event on the posting class |
| One-time data fix | RunBase or a one-shot Job (don't commit Jobs to the model) |
