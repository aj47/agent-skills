# x-twitter-scraper

# X/Twitter Scraper

## Overview
This skill enables scraping X/Twitter content using agent-browser CLI connected to your existing logged-in Chrome session via CDP on port 9222.

## Prerequisites
- agent-browser must be installed globally (`npm install -g agent-browser`)
- Chrome must be running with remote debugging on port 9222 using the permanent debug profile at `~/chrome-debug-profile`

## Chrome Setup (One-Time)

A permanent dedicated debug profile lives at `~/chrome-debug-profile`. Log into X once in that profile and it persists forever.

### Launch Chrome debug session
```bash
chrome-debug
# (alias defined in ~/.zshrc)
```

Or manually:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile" \
  --no-first-run \
  --no-default-browser-check \
  &>/tmp/chrome-debug.log &
sleep 6
curl -s http://localhost:9222/json/version && echo "OK"
```

**Why not `--profile-directory=Default`?** Chrome explicitly blocks remote debugging on the Default profile with: "DevTools remote debugging requires a non-default data directory." The permanent `~/chrome-debug-profile` dir bypasses this while keeping your login session intact across restarts.

**Always use `--cdp 9222`** in all agent-browser commands.

## Verify Login
```bash
agent-browser --cdp 9222 open "https://x.com/home"
sleep 5
agent-browser --cdp 9222 eval --stdin <<'EOF'
document.title + " | logged_in=" + !document.querySelector('[data-testid="loginButton"]')
EOF
# Should show: "(1) Home / X | logged_in=true"
```

If not logged in, open X in the debug Chrome window and log in manually — credentials persist in `~/chrome-debug-profile`.

## Workflow: Scrape Home Feed

### Step 1: Navigate
```bash
agent-browser --cdp 9222 open "https://x.com/home"
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — X never reaches networkidle state.

### Step 2: Extract tweet data via JS eval
```bash
agent-browser --cdp 9222 eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(a => {
    const userEl = a.querySelector('[data-testid="User-Name"]');
    const textEl = a.querySelector('[data-testid="tweetText"]');
    const timeEl = a.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    return {
      user: userEl ? userEl.innerText.replace(/\n/g, ' ') : 'Unknown',
      text: textEl ? textEl.innerText : '',
      time: timeEl ? timeEl.getAttribute('datetime') : '',
      link: linkEl ? 'https://x.com' + linkEl.getAttribute('href') : ''
    };
  }).filter(p => p.text),
  null, 2
)
EVALEOF
```

### Step 3: Switch tabs (For You / Following)
```bash
agent-browser --cdp 9222 snapshot -i
# Find "For you" or "Following" tab ref, then:
agent-browser --cdp 9222 click @<tab-ref>
agent-browser --cdp 9222 wait 3000
# Re-run eval from Step 2
```

### Step 4: Scroll for more content
```bash
agent-browser --cdp 9222 scroll down 2000
agent-browser --cdp 9222 wait 1500
# Re-run eval from Step 2
```

## Workflow: Scrape a Specific Profile

```bash
agent-browser --cdp 9222 open "https://x.com/username"
agent-browser --cdp 9222 wait 5000
agent-browser --cdp 9222 eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll('article[data-testid="tweet"]')).map(a => {
    const textEl = a.querySelector('[data-testid="tweetText"]');
    const timeEl = a.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    return {
      text: textEl ? textEl.innerText : '',
      time: timeEl ? timeEl.getAttribute('datetime') : '',
      link: linkEl ? 'https://x.com' + linkEl.getAttribute('href') : ''
    };
  }).filter(p => p.text),
  null, 2
)
EVALEOF
```

## Best Practices

1. **Always use `--cdp 9222`** — connects to your logged-in Chrome session
2. **Use `~/chrome-debug-profile`** — permanent, stable, no cookie copying needed
3. **Use `chrome-debug` alias** to launch — defined in ~/.zshrc
4. **Always snapshot first** — get current page state before interacting
5. **Use `wait 5000` not `networkidle`** — X never reaches networkidle
6. **Re-snapshot after scrolling** — DOM changes invalidate old refs
7. **Use JS eval for content extraction** — more reliable than snapshot text parsing

## Common Issues

| Problem | Solution |
|---------|----------|
| Not logged in / login page | Open X manually in the debug Chrome window and log in — session persists |
| "DevTools requires non-default data directory" | Don't use `--profile-directory=Default`. Use `--user-data-dir="$HOME/chrome-debug-profile"` |
| Connection refused | Chrome not running — run `chrome-debug` alias |
| `networkidle` timeout | Use `wait 5000` instead — never use `--load networkidle` on X |
| Stale refs | Run `snapshot -i` again after any page change |
| Empty content | Wait longer (8000ms) or scroll — React may not have rendered yet |

## X DOM Selectors Reference
- Tweet article: `article[data-testid="tweet"]`
- Tweet text: `[data-testid="tweetText"]`
- User name block: `[data-testid="User-Name"]`
- Timestamp (with href to tweet): `time` inside an `<a>` tag
- Retweet label: `[data-testid="socialContext"]`
- Like count: `[data-testid="like"] span`

## Related Skills
- **x-post-tweet** — Post tweets using the same CDP approach
- **x-feed-scraper** — Scrape feed with structured output
- **x-feed-summarizer** — Summarize feed content
