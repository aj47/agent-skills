---
name: chrome-debug-session
description: "Launches Chrome with remote debugging port 9222 alongside existing Chrome sessions. Use when asked to 'start chrome debugging', 'connect to chrome', 'launch chrome for browser automation', or before any agent-browser --cdp 9222 commands."
---

# Chrome Debug Session

Launch a second Chrome instance with `--remote-debugging-port=9222` using a pre-made profile at `~/chrome-debug-profile`. No need to kill existing Chrome sessions.

## Step 1: Check if already running
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```
If this returns JSON, debug Chrome is already up — skip to using it.

## Step 2: Launch debug Chrome alongside existing Chrome
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile" &
sleep 5
```
This works because the debug instance uses a different user-data-dir than the default Chrome, so macOS treats them as separate processes.

## Step 3: Verify
```bash
curl -s --max-time 5 http://localhost:9222/json/version
```
Should return JSON with `Browser` and `webSocketDebuggerUrl`.

## Usage with agent-browser
```bash
agent-browser --cdp 9222 open https://example.com
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 eval "document.title"
```

## Troubleshooting
| Problem | Fix |
|---------|-----|
| Port 9222 not responding | Check `lsof -i :9222` and `pgrep -la Chrome` |
| Opens tab in existing Chrome instead | Ensure `--user-data-dir` points to `~/chrome-debug-profile` (not default path) |
| Stale logins | Re-copy profile: `cp -r "$HOME/Library/Application Support/Google/Chrome" ~/chrome-debug-profile` |

## Platform
- macOS only
- Requires `~/chrome-debug-profile` (pre-copied Chrome profile with login sessions)
