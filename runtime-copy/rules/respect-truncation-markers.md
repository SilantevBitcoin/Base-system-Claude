# Respect truncation and pagination markers in tool results

When any tool result contains a marker indicating the output is truncated or paginated, that marker is an **objective signal that I am not seeing everything**. I must not silently proceed as if I see the full result.

## Triggers (any of these in tool output)

- `[Showing results with pagination = limit: N]`
- `[truncated]`, `... (truncated)`, `... (X more lines)`
- `Showing first N of M`
- `head_limit` was applied and the result count equals the limit
- WebFetch / WebSearch returned "summarized" or "results may be summarized"
- Any explicit `...` ellipsis the tool itself prints to mark omitted content

## Required action

Before using the (partial) result to form an answer, do **one** of these:

1. **Re-query without the limit** — re-run with `head_limit: 0` (unlimited), or with `offset: N` to get the next page, or with a tighter filter so the full result fits.
2. **Explicitly tell the user** the result was truncated and what I might be missing. Example: "Grep showed first 60 of likely more matches; if X isn't in these, I need to re-query."

Picking option 2 is fine when re-querying is expensive or unnecessary. Picking neither — silently using a partial result as if it were complete — is the failure mode.

## Why this rule exists

2026-05-28: I grepped for `video|mp4` in landing files, got back 60 lines with the literal marker `[Showing results with pagination = limit: 60]`. I ignored the marker and built an answer assuming I saw all video references. The truncated lines contained `section3-*` files (the actual videos for page 2), so my answer was about `section2-*` (which I'd seen) — wrong files, wrong dimensions, wrong durations. The user caught it; if they hadn't, we would have acted on bad data.

The rule is not "always re-query" — the rule is "never silently treat a partial result as complete."

## How to apply

After every tool call, before writing the answer:
- Scan the result for the trigger markers above (this is a one-second visual scan, not a deep check).
- If found: either re-query or write the disclaimer in the answer.
- If not found: proceed normally.
