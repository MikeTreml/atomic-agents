# Extension vs. Over-layering

In D365 F&O, the modern customization model is **extension** — you ship a custom model that augments OOB code via class extensions, event handlers, and metadata extensions. Over-layering — editing OOB code directly — is supported only for legacy compatibility and creates a one-way ticket out of clean upgrades.

If you remember nothing else: **do not over-layer**. If a new file would land inside `ApplicationSuite/`, `ApplicationFoundation/`, or another standard model, stop.

## Why over-layering hurts

- **Upgrades break.** Microsoft ships new OOB code. Your over-layered version conflicts; the merge is manual; reviewers can't tell what was customized.
- **No visibility.** A reviewer looking at `SalesTable.validateWrite()` doesn't know your over-layer changed it unless they switch model context.
- **Locks you to a version.** Over-layered code is keyed to the OOB version it sat on top of. Moving to a new minor release forces a re-merge.
- **Microsoft is removing it.** OOB models in F&O are increasingly **sealed** — over-layering them is no longer possible. Even where it still works, the platform discourages it.

## What extension gives you

- **A custom model.** Your code lives in `<YourModel>/`, owned by you, versioned by you, deployed by you.
- **Augmentation, not modification.** Your code adds behavior. Base behavior keeps working.
- **Upgrade simplicity.** When Microsoft ships a new release, your augmenter usually just keeps working — you only re-test it.
- **Discoverable customization.** A reviewer looking at the OOB code searches for `ExtensionOf(classStr(Target))` across your model and finds every augmentation.

## The mapping

| Old (over-layering) | New (extension) |
|---|---|
| Edit a method on `SalesTableType` | `[ExtensionOf(classStr(SalesTableType))]` augmenter class with CoC |
| Add a field to `CustTable` | Table extension XML + augmenter class for the field's `display`/`edit`/`init` methods |
| Add a control to a form | Form extension XML + form augmenter class for control behavior |
| Modify base behavior on save | CoC on `validateWrite()` / `update()` — or a `DataEventHandler` post-`Written` |
| Hook a posting event | Subscribe to the Pre/Post event the posting class exposes |
| Add a button | Form extension XML for the button + `FormControlEventHandler` for the click |

## Migrating over-layered code

If you've inherited an over-layered codebase:

1. **Inventory.** Find every over-layered file (anything in an OOB model that isn't OOB).
2. **Categorize by mechanism.**
   - Method body changes → CoC handler in a new augmenter class.
   - Method body changes that *replace* the base → CoC handler that does **not** call `next` (be very deliberate).
   - Field additions → table extension.
   - Control additions → form extension.
   - New methods → put them on a helper class in your model, not on the OOB class.
3. **Move incrementally.** One method or field at a time. Keep the over-layered code in place while moving so the system runs, then delete it once the extension is verified.
4. **Re-test against the OOB tests** (if any) plus any of your own.

## Sealed classes / methods

Some OOB classes and methods are sealed — explicitly marked `final` so CoC can't augment them. When you hit one:

- First, ask if you really need to extend that exact method. Often a nearby method or a different layer is the real extension point.
- If you genuinely do need it, file the request with Microsoft to unseal. Don't try to work around it with reflection or other tricks.
- In the meantime, build adjacent — e.g. CoC the caller instead of the sealed method itself.

## Code-review red flags

- A file under an OOB model directory in a custom commit.
- An `[ExtensionOf]` attribute pointing at your own custom class (extension of an extension is fine but check the chain order).
- A method body that catches and silently swallows exceptions to "make the base behavior work" — usually a sign that the wrong extension point was chosen.

## The one paragraph version

**Make your model. Extend OOB. Augment, don't replace. Use events when you only need to react. Use CoC when you need to wrap. Over-layering is a debt instrument — every time you do it, you owe future-you a re-merge.**
