# x-twitter-scraper

# X/Twitter Scraper

## Overview
This skill enables scraping X/Twitter content using agent-browser CLI connected to your existing logged-in Chrome session via CDP on port 9222. Always use `--cdp 9222` — never use `--auto-connect` or open a new browser, as that will not be logged in.

## Prerequisites
- agent-browser must be installed globally (`npm install -g agent-browser`)
- Chrome must be running with remote debugging enabled (port 9222)
- User must be logged into X/Twitter in Chrome

## Quick Setup
```bash
# Verify Chrome is running with debugging on port 9222
curl -s --max-time 3 http://localhost:9222/json/version

# If not running, launch Chrome with debugging:
open -a "Google Chrome" --args --remote-debugging-port=9222 --profile-directory=Default
sleep 3
```

**IMPORTANT: Always use `--cdp 9222`** to connect to the user's existing logged-in Chrome session. Never use `--auto-connect` or omit the flag — those open a fresh unauthenticated browser.

## Workflow: Scrape Following Tab (Default)

### Step 1: Verify Chrome and navigate
```bash
curl -s --max-time 3 http://localhost:9222/json/version
agent-browser --cdp 9222 open "https://x.com/home"
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — X never reaches networkidle state. Use fixed `wait 5000`.

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

1. **Always use `--cdp 9222`** — this connects to your logged-in Chrome session
2. **Always snapshot first** — get current page state before interacting
3. **Use `wait 5000` not `networkidle`** — X never reaches networkidle
4. **Use `-i` flag for navigation** — `snapshot -i` shows interactive elements only
5. **Re-snapshot after scrolling** — DOM changes invalidate old refs
6. **Use JS eval for content extraction** — more reliable than snapshot text parsing

## Common Issues

| Problem | Solution |
|---------|----------|
| Not logged in | Make sure you're using `--cdp 9222`, not `--auto-connect` |
| Connection refused | Launch Chrome with `--remote-debugging-port=9222` |
| `networkidle` timeout | Use `wait 5000` instead — never use `--load networkidle` on X |
| Stale refs | Run `snapshot -i` again after any page change |
| Empty content | Wait longer (8000ms) or scroll — React may not have rendered yet |
| Rate limiting | Wait before continuing if X shows errors |

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
