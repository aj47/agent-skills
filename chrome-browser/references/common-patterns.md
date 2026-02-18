# Common Patterns

Practical patterns for browser automation via `agent-browser --cdp 9222`.

**Related**: [../SKILL.md](../SKILL.md) for core workflow, [commands.md](commands.md) for full reference, [snapshot-refs.md](snapshot-refs.md) for ref details.

## Form Submission

```bash
agent-browser --cdp 9222 open https://example.com/signup
agent-browser --cdp 9222 snapshot -i
# @e1 [input] "Name", @e2 [input] "Email", @e3 [select] "State", @e4 [checkbox], @e5 [button] "Submit"

agent-browser --cdp 9222 fill @e1 "Jane Doe"
agent-browser --cdp 9222 fill @e2 "jane@example.com"
agent-browser --cdp 9222 select @e3 "California"
agent-browser --cdp 9222 check @e4
agent-browser --cdp 9222 click @e5
agent-browser --cdp 9222 wait --load networkidle
agent-browser --cdp 9222 snapshot -i  # Verify result
```

## Data Extraction

```bash
# Get text from specific element
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 get text @e5

# Dump all page text
agent-browser --cdp 9222 get text body > page.txt

# JSON output for programmatic parsing
agent-browser --cdp 9222 snapshot -i --json
agent-browser --cdp 9222 get text @e1 --json
```

## JavaScript Evaluation

Shell quoting can corrupt complex JS — use `--stdin` or `-b` to avoid issues.

```bash
# Simple expressions — regular quoting is fine
agent-browser --cdp 9222 eval 'document.title'
agent-browser --cdp 9222 eval 'document.querySelectorAll("img").length'

# Complex JS — use heredoc with --stdin (RECOMMENDED)
agent-browser --cdp 9222 eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll("img"))
    .filter(i => !i.alt)
    .map(i => ({ src: i.src.split("/").pop(), width: i.width }))
)
EVALEOF

# Alternative — base64 encoding (avoids all shell escaping)
agent-browser --cdp 9222 eval -b "$(echo -n 'Array.from(document.querySelectorAll("a")).map(a => a.href)' | base64)"
```

**Rules of thumb:**
- Single-line, no nested quotes → regular `eval 'expression'` with single quotes
- Nested quotes, arrow functions, template literals → use `eval --stdin <<'EVALEOF'`
- Programmatic/generated scripts → use `eval -b` with base64

## Command Chaining

Commands can be chained with `&&` since the browser persists via a background daemon:

```bash
# Navigate + wait + snapshot in one call
agent-browser --cdp 9222 open https://example.com && \
agent-browser --cdp 9222 wait --load networkidle && \
agent-browser --cdp 9222 snapshot -i

# Chain multiple fills
agent-browser --cdp 9222 fill @e1 "user@example.com" && \
agent-browser --cdp 9222 fill @e2 "password123" && \
agent-browser --cdp 9222 click @e3
```

**When to chain:** Use `&&` when you don't need intermediate output (e.g., open + wait + screenshot). Run separately when you need to parse output first (e.g., snapshot to discover refs, then interact).

## Ref Lifecycle (Important)

Refs (`@e1`, `@e2`, etc.) are **invalidated when the page changes**. Always re-snapshot after:

- Clicking links or buttons that navigate
- Form submissions
- Dynamic content loading (dropdowns, modals, infinite scroll)

```bash
agent-browser --cdp 9222 click @e5       # Navigates to new page
agent-browser --cdp 9222 snapshot -i     # MUST re-snapshot — old refs are gone
agent-browser --cdp 9222 click @e1       # Use new refs
```

## Scrolling and Lazy-Loaded Content

```bash
# Scroll to reveal more content
agent-browser --cdp 9222 scroll down 1000
agent-browser --cdp 9222 wait 1000       # Wait for lazy content to load
agent-browser --cdp 9222 snapshot -i     # Get refs for newly visible elements

# Scroll a specific element into view
agent-browser --cdp 9222 scrollintoview @e15
```

## Handling Slow/Streaming Sites

Some sites (e.g. X/Twitter, SPAs with websockets) never reach `networkidle`:

```bash
# DON'T — this will hang
agent-browser --cdp 9222 wait --load networkidle

# DO — use a fixed wait instead
agent-browser --cdp 9222 wait 5000
agent-browser --cdp 9222 snapshot -i
```

## Screenshots and PDFs

```bash
# Quick screenshot
agent-browser --cdp 9222 screenshot

# Full page capture
agent-browser --cdp 9222 screenshot --full output.png

# Save as PDF
agent-browser --cdp 9222 pdf output.pdf
```

## Tabs

```bash
agent-browser --cdp 9222 tab                 # List open tabs
agent-browser --cdp 9222 tab new https://x.com  # Open new tab
agent-browser --cdp 9222 tab 2               # Switch to tab 2
agent-browser --cdp 9222 tab close           # Close current tab
```

