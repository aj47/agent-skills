# Snapshot and Refs

How element references work, their lifecycle, and best practices.

**Related**: [../SKILL.md](../SKILL.md) for core workflow, [commands.md](commands.md) for full command reference.

## How Refs Work

Traditional approach:
```
Full DOM/HTML → AI parses → CSS selector → Action (~3000-5000 tokens)
```

agent-browser approach:
```
Compact snapshot → @refs assigned → Direct interaction (~200-400 tokens)
```

## The Snapshot Command

```bash
# Interactive snapshot — RECOMMENDED for most tasks
agent-browser --cdp 9222 snapshot -i

# Include cursor-interactive elements (divs with onclick, cursor:pointer)
agent-browser --cdp 9222 snapshot -i -C

# Full accessibility tree (verbose)
agent-browser --cdp 9222 snapshot

# Scope to a specific container
agent-browser --cdp 9222 snapshot -s "#main"
agent-browser --cdp 9222 snapshot @e9       # Scope to a ref
```

### Output Format

```
Page: Example Site - Home
URL: https://example.com

@e1 [header]
  @e2 [nav]
    @e3 [a] "Home"
    @e4 [a] "Products"
    @e5 [a] "About"
  @e6 [button] "Sign In"

@e7 [main]
  @e8 [h1] "Welcome"
  @e9 [form]
    @e10 [input type="email"] placeholder="Email"
    @e11 [input type="password"] placeholder="Password"
    @e12 [button type="submit"] "Log In"
```

### Ref Notation

```
@e1 [tag type="value"] "text content" placeholder="hint"
│    │   │             │               │
│    │   │             │               └─ Additional attributes
│    │   │             └─ Visible text
│    │   └─ Key attributes
│    └─ HTML tag name
└─ Unique ref ID
```

## Ref Lifecycle

**Refs are invalidated when the page changes.** This is the #1 source of errors.

### When refs invalidate:
- Page navigation (clicking links, form submissions)
- DOM changes (opening dropdowns, modals, dynamic content loading)
- Page reload

### Correct pattern:

```bash
agent-browser --cdp 9222 snapshot -i     # Get refs
agent-browser --cdp 9222 click @e5       # Navigates to new page
agent-browser --cdp 9222 snapshot -i     # MUST re-snapshot
agent-browser --cdp 9222 click @e1       # Use NEW refs
```

### Wrong pattern:

```bash
agent-browser --cdp 9222 snapshot -i     # Get refs
agent-browser --cdp 9222 click @e5       # Navigates to new page
agent-browser --cdp 9222 click @e1       # BROKEN — @e1 is stale!
```

## Best Practices

### 1. Always snapshot before interacting

```bash
# CORRECT
agent-browser --cdp 9222 open https://example.com
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 click @e1

# WRONG — ref doesn't exist yet
agent-browser --cdp 9222 open https://example.com
agent-browser --cdp 9222 click @e1
```

### 2. Re-snapshot after dynamic changes

```bash
agent-browser --cdp 9222 click @e1       # Opens dropdown
agent-browser --cdp 9222 snapshot -i     # See dropdown items
agent-browser --cdp 9222 click @e7       # Select item
```

### 3. Scope snapshots on complex pages

```bash
# Too many elements? Scope to just the form
agent-browser --cdp 9222 snapshot @e9
```

### 4. Use get text for content extraction (not snapshot)

```bash
# Snapshot is for finding interactive elements
# Use get text when you just need content
agent-browser --cdp 9222 get text @e5
```

## Semantic Locators (Alternative to Refs)

When refs are unavailable or unreliable:

```bash
agent-browser --cdp 9222 find text "Sign In" click
agent-browser --cdp 9222 find label "Email" fill "user@test.com"
agent-browser --cdp 9222 find role button click --name "Submit"
agent-browser --cdp 9222 find placeholder "Search" type "query"
agent-browser --cdp 9222 find testid "submit-btn" click
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Ref not found" | Re-snapshot — refs likely invalidated by a page change |
| Element not in snapshot | Scroll down (`scroll down 1000`) then re-snapshot |
| Too many elements | Scope snapshot to a container: `snapshot @e5` or `snapshot -s "#main"` |
| Dynamic content missing | Wait first (`wait 2000`) then snapshot |

