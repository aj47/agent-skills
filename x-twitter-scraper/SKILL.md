# x-twitter-scraper

# X/Twitter Scraper

## Overview
This skill enables scraping X/Twitter content using agent-browser CLI connected to your existing logged-in Chrome session via CDP on port 9222.

## Prerequisites
- agent-browser must be installed globally (`npm install -g agent-browser`)
- Chrome must be running with remote debugging on port 9222 using a non-default user-data-dir that contains your X cookies

## Chrome Setup (IMPORTANT)

Chrome refuses to enable remote debugging on the Default profile directly. You must copy the Default profile cookies to a temp dir and launch from there:

```bash
# Step 1: Kill any existing debug Chrome
pkill -f "Google Chrome.*remote-debugging-port=9222" 2>/dev/null; sleep 1

# Step 2: Copy Default profile cookies to temp dir
mkdir -p /tmp/chrome-debug-profile/Default
cp ~/Library/Application\ Support/Google/Chrome/Default/Cookies /tmp/chrome-debug-profile/Default/ 2>/dev/null || true
cp ~/Library/Application\ Support/Google/Chrome/Default/Network/Cookies /tmp/chrome-debug-profile/Default/ 2>/dev/null || true
cp ~/Library/Application\ Support/Google/Chrome/Default/Login\ Data /tmp/chrome-debug-profile/Default/ 2>/dev/null || true
cp ~/Library/Application\ Support/Google/Chrome/Default/Preferences /tmp/chrome-debug-profile/Default/ 2>/dev/null || true

# Step 3: Launch Chrome with debug port using the temp profile
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug-profile \
  --no-first-run \
  --no-default-browser-check \
  &>/tmp/chrome-debug.log &

sleep 8

# Step 4: Verify
curl -s --max-time 5 http://localhost:9222/json/version && echo "OK"
```

**Why this works:** Chrome's Default profile is locked from remote debugging as a security measure. Copying cookies to a fresh user-data-dir bypasses this while keeping your login session intact.

**Why NOT `--profile-directory=Default`:** Chrome ignores `--remote-debugging-port` when using the real Default profile and prints: "DevTools remote debugging requires a non-default data directory."

**Always use `--cdp 9222`** in all agent-browser commands — never use `--auto-connect`.

## Verify Login
```bash
agent-browser --cdp 9222 open "https://x.com/home"
sleep 5
agent-browser --cdp 9222 eval --stdin <<'EOF'
document.title + " | logged_in=" + !document.querySelector('[data-testid="loginButton"]')
EOF
# Should show: "(1) Home / X | logged_in=true"
```

## Workflow: Scrape Following Tab (Default)

### Step 1: Navigate
```bash
agent-browser --cdp 9222 open "https://x.com/home"
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — X never reaches networkidle state.

### Step 2: Snapshot to find tabs
```bash
agent-browser --cdp 9222 snapshot -i
```

### Step 3: Click Following tab
From snapshot, find the "Following" tab ref and click it:
```bash
agent-browser --cdp 9222 click @<following-tab-ref>
agent-browser --cdp 9222 wait 3000
```

### Step 4: Extract tweet data via JS eval
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

### Step 5: Scroll for more content
```bash
agent-browser --cdp 9222 scroll down 2000
agent-browser --cdp 9222 wait 1500
# repeat eval from Step 4
```

## Workflow: Scrape For You Tab

```bash
agent-browser --cdp 9222 open "https://x.com/home"
agent-browser --cdp 9222 wait 5000
agent-browser --cdp 9222 snapshot -i
# Click "For you" tab from the snapshot refs
agent-browser --cdp 9222 click @<foryou-tab-ref>
agent-browser --cdp 9222 wait 3000
# Run JS eval from Step 4 above
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
2. **Launch Chrome with `/tmp/chrome-debug-profile`** — not `--profile-directory=Default`
3. **Always snapshot first** — get current page state before interacting
4. **Use `wait 5000` not `networkidle`** — X never reaches networkidle
5. **Re-snapshot after scrolling** — DOM changes invalidate old refs
6. **Use JS eval for content extraction** — more reliable than snapshot text parsing

## Common Issues

| Problem | Solution |
|---------|----------|
| Not logged in / login page | Chrome launched with wrong profile or `/tmp/chrome-debug` (empty). Re-run Chrome Setup above. |
| "DevTools requires non-default data directory" | Don't use `--profile-directory=Default`. Use `--user-data-dir=/tmp/chrome-debug-profile` with copied cookies. |
| Connection refused | Chrome not running — run Chrome Setup steps |
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
