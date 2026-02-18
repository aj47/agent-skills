# Command Reference

Complete reference for all `agent-browser --cdp 9222` commands. For quick start, see [../SKILL.md](../SKILL.md).

**Note**: All commands below assume `--cdp 9222` to connect to your logged-in Chrome. Shown without the flag for brevity — always prepend `agent-browser --cdp 9222`.

## Navigation

```bash
open <url>              # Navigate to URL (aliases: goto, navigate)
back                    # Go back
forward                 # Go forward
reload                  # Reload page
close                   # Close browser
```

## Snapshot

```bash
snapshot                # Full accessibility tree
snapshot -i             # Interactive elements only (RECOMMENDED)
snapshot -i -C          # Include cursor-interactive elements
snapshot -c             # Compact output
snapshot -d 3           # Limit depth to 3
snapshot -s "#main"     # Scope to CSS selector
snapshot @e9            # Scope to a ref
```

## Interactions

```bash
click @e1               # Click
click @e1 --new-tab     # Click and open in new tab
dblclick @e1            # Double-click
focus @e1               # Focus element
fill @e2 "text"         # Clear and type
type @e2 "text"         # Type without clearing
press Enter             # Press key
press Control+a         # Key combination
hover @e1               # Hover
check @e1               # Check checkbox
uncheck @e1             # Uncheck checkbox
select @e1 "value"      # Select dropdown option
select @e1 "a" "b"      # Select multiple options
scroll down 500         # Scroll page (default: down 300px)
scrollintoview @e1      # Scroll element into view
drag @e1 @e2            # Drag and drop
upload @e1 file.pdf     # Upload files
```

## Get Information

```bash
get text @e1            # Get element text
get html @e1            # Get innerHTML
get value @e1           # Get input value
get attr @e1 href       # Get attribute
get title               # Get page title
get url                 # Get current URL
get count ".item"       # Count matching elements
get box @e1             # Get bounding box
get styles @e1          # Get computed styles
```

## Check State

```bash
is visible @e1          # Check if visible
is enabled @e1          # Check if enabled
is checked @e1          # Check if checked
```

## Screenshots and PDF

```bash
screenshot              # Save to temp directory
screenshot path.png     # Save to specific path
screenshot --full       # Full page screenshot
pdf output.pdf          # Save as PDF
```

## Wait

```bash
wait @e1                # Wait for element
wait 2000               # Wait milliseconds
wait --text "Success"   # Wait for text
wait --url "**/page"    # Wait for URL pattern
wait --load networkidle # Wait for network idle
wait --fn "window.ready" # Wait for JS condition
```

## Mouse Control

```bash
mouse move 100 200      # Move mouse
mouse down left         # Press button
mouse up left           # Release button
mouse wheel 100         # Scroll wheel
```

## Semantic Locators

```bash
find role button click --name "Submit"
find text "Sign In" click
find text "Sign In" click --exact
find label "Email" fill "user@test.com"
find placeholder "Search" type "query"
find testid "submit-btn" click
find first ".item" click
find nth 2 "a" hover
```

## Tabs

```bash
tab                     # List tabs
tab new [url]           # New tab
tab 2                   # Switch to tab by index
tab close               # Close current tab
tab close 2             # Close tab by index
```

## Cookies and Storage

```bash
cookies                 # Get all cookies
cookies set name value  # Set cookie
cookies clear           # Clear cookies
storage local           # Get all localStorage
storage local key       # Get specific key
storage local set k v   # Set value
storage local clear     # Clear all
```

## JavaScript

```bash
eval "document.title"          # Simple expression
eval -b "<base64>"             # Base64-encoded JS
eval --stdin                   # Read script from stdin
```

Use `--stdin` or `-b` for anything with nested quotes or special characters. See [common-patterns.md](common-patterns.md#javascript-evaluation) for examples.

## State Management

```bash
state save auth.json    # Save cookies, storage, auth state
state load auth.json    # Restore saved state
```

