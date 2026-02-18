---
name: x-twitter-scraper
description: "Scrapes X/Twitter content from any profile or feed tab. Use when asked to scrape a specific Twitter user, get tweets from a profile, or extract X content beyond the Following feed."
---

# X/Twitter Scraper

## Overview
Scrapes X/Twitter content using agent-browser CLI connected to your existing logged-in Chrome session via CDP on port 9222. Handles Following feed, For You feed, and individual profile scraping.

## Prerequisites

Requires **chrome-browser** skill to be running first. Verify:
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```

**IMPORTANT: Always use `--cdp 9222`** to connect to your logged-in Chrome. Never use `--auto-connect` — that opens a fresh unauthenticated browser.

## Workflow: Scrape Following Tab (Default)

### Step 1: Navigate
```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — X never reaches networkidle. Use fixed `wait 5000`.

### Step 2: Click Following tab
```bash
agent-browser --cdp 9222 snapshot -i
# Find "Following" tab ref from snapshot
agent-browser --cdp 9222 click <ref>
agent-browser --cdp 9222 wait 3000
```

### Step 3: Extract tweet data via JS eval
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

### Step 4: Scroll for more
```bash
agent-browser --cdp 9222 scroll down 2000
agent-browser --cdp 9222 wait 1500
# repeat eval from Step 3
```

## Workflow: Scrape For You Tab

```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 5000
agent-browser --cdp 9222 snapshot -i
# Click "For you" tab from the snapshot refs
agent-browser --cdp 9222 click <foryou-tab-ref>
agent-browser --cdp 9222 wait 3000
# Run JS eval from Step 3 above
```

## Workflow: Scrape a Specific Profile

```bash
agent-browser --cdp 9222 open https://x.com/username
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
2. **Always snapshot first** — get current page state before interacting
3. **Use `wait 5000` not `networkidle`** — X never reaches networkidle
4. **Use `-i` flag** — `snapshot -i` shows interactive elements only
5. **Re-snapshot after scrolling** — DOM changes invalidate old refs
6. **Use JS eval for content extraction** — more reliable than snapshot text parsing

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Not logged in | Use `--cdp 9222`, not `--auto-connect` |
| Connection refused | Run chrome-browser skill first |
| `networkidle` timeout | Use `wait 5000` — never use `--load networkidle` on X |
| Stale refs | Run `snapshot -i` again after any page change |
| Empty content | Wait longer (8000ms) or scroll — React may not have rendered |
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
- **chrome-browser** — Launch Chrome with CDP debugging
