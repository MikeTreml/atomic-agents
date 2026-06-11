# Chain of Command — Patterns

Chain of Command (CoC) lets you wrap a method on an existing class, table, or form without over-layering. The augmenter class declares a method with the same signature and calls `next` to invoke the previous implementation in the chain.

## The shape

```xpp
[ExtensionOf(classStr(Target))]
final class Prefix_Target_Extension
{
    public <ReturnType> <MethodName>(<args>)
    {
        // optional: pre-work
        <ReturnType> ret = next <MethodName>(<args>);
        // optional: post-work
        return ret;
    }
}
```

**Hard requirements:**
- `[ExtensionOf(...)]` must use the correct identifier helper: `classStr`, `formStr`, `tableStr`, `formDataSourceStr(F, DS)`, `formControlStr(F, C)`.
- The class is `final`. It has no fields. It can only contain CoC methods (and helper privates).
- Return type, name, and parameter types/order match the augmented method **exactly**.
- Use `next <MethodName>(args)` to call the next implementation in the chain. If you omit it, you've silently replaced the base behavior.

## Pre-work pattern

```xpp
public boolean checkUpdate()
{
    if (!this.Acme_isPreflightDone)
    {
        return checkFailed("Pre-flight is required before update.");
    }
    return next checkUpdate();
}
```

Use when you want to short-circuit the chain on a validation failure. Always return the right type; `checkFailed` returns `false`.

## Post-work pattern

```xpp
public boolean validateWrite()
{
    boolean ret = next validateWrite();
    if (ret)
    {
        ret = this.acmeCustomCheck();
    }
    return ret;
}
```

Use when you want to **augment** the base result, not override it. The base check stays authoritative.

## Wrap-around pattern

```xpp
public void post()
{
    Acme_PostingTelemetry::start(this);
    try
    {
        next post();
    }
    finally
    {
        Acme_PostingTelemetry::stop(this);
    }
}
```

Use for instrumentation. Always wrap `next` in try/finally so telemetry stops even if posting throws.

## Replace pattern (rare — be explicit)

```xpp
public boolean canBePosted()
{
    // Intentionally replaces base check; see ticket ACME-123.
    return Acme_PostingRules::isAllowedFor(this);
}
```

Do this **only when**:
- The base method's logic is provably wrong for your scenario, AND
- You've documented why, AND
- You've considered whether a different extension point (event, separate method) is more appropriate.

When you do it, leave a comment explaining the intentional replacement.

## Common mistakes

1. **Forgetting `next`.** The augmenter silently replaces the base method. Hard to debug because everything compiles.
2. **Calling `next` more than once.** The chain advances each time; the second call invokes the implementation *before* the previous one. Almost never what you want.
3. **Wrong identifier helper.** `[ExtensionOf(formStr(MyClass))]` when the target is a class won't bind at runtime — and the compiler doesn't warn loudly enough.
4. **Signature drift.** Augmenting `boolean validateWrite()` with `public void validateWrite()` won't be recognized as the same method.
5. **State on the augmenter.** Adding fields turns the augmenter into stateful logic; that's not how CoC works. Use a helper class or static cache instead.
6. **CoC over an OOB method that already has a Pre/Post event.** Prefer the event subscriber — less coupling, easier to remove.

## When CoC isn't right

Use an **event subscriber** when:
- You only want to react after the base method completes.
- You don't need the return value to influence further logic.
- You'd otherwise write a CoC method that just calls `next` and then does work.

Use a **new method** on a helper class when:
- The work is reusable across multiple call sites.
- It would otherwise duplicate across several CoC augmenters.

Use **over-layering** never. The platform supports it for compatibility but it's a one-way ticket out of the modern upgrade story.

## Discoverability

To check whether the method you want to augment has Pre/Post events, search the OOB code for the event-handler attribute string. If a Post event exists, prefer subscribing to it. If only the method exists, CoC is the right tool.
