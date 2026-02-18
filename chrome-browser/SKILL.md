---
name: chrome-browser
description: "Browser automation using agent-browser CLI connected to a logged-in Chrome session via CDP. Use when asked to browse a website, fill forms, click buttons, take screenshots, scrape data, automate browser tasks, or any web interaction. Also use when asked to 'start chrome debugging', 'connect to chrome', or 'launch chrome for browser automation'."
---

# Browser Automation via Chrome Debug Session

Browse the web, fill forms, scrape data, and automate any browser task using `agent-browser` connected to your logged-in Chrome session via CDP on port 9222.

**Always use `--cdp 9222`** to connect to your existing Chrome with saved logins. Never use `--auto-connect` — that opens a fresh unauthenticated browser.

## Core Workflow

Every browser task follows this loop:

1. **Navigate**: `agent-browser --cdp 9222 open <url>`
2. **Snapshot**: `agent-browser --cdp 9222 snapshot -i` (get element refs like `@e1`, `@e2`)
3. **Interact**: Use refs to click, fill, select
4. **Re-snapshot**: After any page change, get fresh refs (they invalidate on DOM changes)

```bash
agent-browser --cdp 9222 open https://example.com/form
agent-browser --cdp 9222 snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser --cdp 9222 fill @e1 "user@example.com"
agent-browser --cdp 9222 fill @e2 "password123"
agent-browser --cdp 9222 click @e3
agent-browser --cdp 9222 wait --load networkidle
agent-browser --cdp 9222 snapshot -i  # Check result
```

## Essential Commands

```bash
# Navigation
agent-browser --cdp 9222 open <url>          # Navigate to URL
agent-browser --cdp 9222 back                # Go back
agent-browser --cdp 9222 reload              # Reload page

# Snapshot
agent-browser --cdp 9222 snapshot -i         # Interactive elements with refs (recommended)
agent-browser --cdp 9222 snapshot -i -C      # Include cursor-interactive elements

# Interaction (use @refs from snapshot)
agent-browser --cdp 9222 click @e1           # Click element
agent-browser --cdp 9222 fill @e2 "text"     # Clear and type text
agent-browser --cdp 9222 type @e2 "text"     # Type without clearing
agent-browser --cdp 9222 select @e1 "option" # Select dropdown option
agent-browser --cdp 9222 press Enter         # Press key
agent-browser --cdp 9222 scroll down 500     # Scroll page

# Get information
agent-browser --cdp 9222 get text @e1        # Get element text
agent-browser --cdp 9222 get url             # Get current URL
agent-browser --cdp 9222 get title           # Get page title

# Wait
agent-browser --cdp 9222 wait @e1            # Wait for element
agent-browser --cdp 9222 wait --load networkidle  # Wait for network idle
agent-browser --cdp 9222 wait 2000           # Wait milliseconds

# Capture
agent-browser --cdp 9222 screenshot          # Screenshot to temp dir
agent-browser --cdp 9222 screenshot out.png  # Screenshot to specific path
agent-browser --cdp 9222 screenshot --full   # Full page screenshot
```

## Chrome Setup (with Saved Logins)

This uses a pre-made Chrome profile at `~/chrome-debug-profile` that preserves your login sessions. The debug instance runs alongside your regular Chrome.

### Check if already running
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```
If this returns JSON, Chrome is already up — skip to browsing.

### Launch debug Chrome
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile" &
sleep 5
```
Uses a separate `--user-data-dir` so macOS treats it as an independent process from your daily Chrome.

### Verify
```bash
curl -s --max-time 5 http://localhost:9222/json/version
```
Should return JSON with `Browser` and `webSocketDebuggerUrl`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 9222 not responding | Check `lsof -i :9222` and `pgrep -la Chrome` |
| Opens tab in existing Chrome instead | Ensure `--user-data-dir` points to `~/chrome-debug-profile` (not default path) |
| Stale logins | Re-copy profile: `cp -r "$HOME/Library/Application Support/Google/Chrome" ~/chrome-debug-profile` |
| Not logged in to a site | Use the debug Chrome window to log in manually, sessions persist in the profile |
| `networkidle` times out | Some sites (e.g. X/Twitter) never reach networkidle — use `wait 5000` instead |

## Platform
- macOS only
- Requires `~/chrome-debug-profile` (pre-copied Chrome profile with login sessions)

## Deep-Dive References

| Reference | When to Use |
|-----------|-------------|
| [references/common-patterns.md](references/common-patterns.md) | Form filling, data extraction, JS eval, command chaining |
| [references/commands.md](references/commands.md) | Full command reference with all options |
| [references/snapshot-refs.md](references/snapshot-refs.md) | Ref lifecycle, invalidation rules, troubleshooting |
| [references/authentication.md](references/authentication.md) | Login flows, OAuth, state persistence |
