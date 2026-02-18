---
name: x-feed-summarizer
description: "Summarize X/Twitter feed quickly, including key links. Triggers: 'summarize my feed', 'what's on X', 'twitter summary', 'what's trending'"
---

# X/Twitter Feed Summarizer

Fast extraction and summarization of X feed content using agent-browser CDP connected to your existing logged-in Chrome session via CDP on port 9222.

**IMPORTANT: Always use `--cdp 9222`** to connect to your logged-in Chrome. Never use `--auto-connect` or a fresh browser — you won't be logged in.

## Prerequisites

Requires **chrome-debug-session** skill to be running first. Verify:
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```

## Quick Workflow

### Step 1: Navigate
```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — X never reaches networkidle. Use fixed `wait 5000`.

### Step 2: Click Following tab
```bash
agent-browser --cdp 9222 snapshot -i
# Find "Following" tab ref from snapshot, e.g. e12
agent-browser --cdp 9222 click e12
agent-browser --cdp 9222 wait 3000
```

### Step 3: Extract posts with links (gets ~12 posts)
```bash
agent-browser --cdp 9222 eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll('article[data-testid="tweet"]')).slice(0, 12).map((a, i) => {
    const userEl = a.querySelector('[data-testid="User-Name"]');
    const textEl = a.querySelector('[data-testid="tweetText"]');
    const timeEl = a.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    const links = Array.from(a.querySelectorAll('a[href]'))
      .map(l => ({ text: l.innerText.trim().slice(0, 50), href: l.href }))
      .filter(l => l.text && l.href.includes('x.com'));
    return {
      i,
      user: userEl ? userEl.innerText.replace(/\n/g, ' ') : 'Unknown',
      text: textEl ? textEl.innerText.slice(0, 400) : '',
      time: timeEl ? timeEl.getAttribute('datetime') : '',
      link: linkEl ? 'https://x.com' + linkEl.getAttribute('href') : '',
      links
    };
  }).filter(p => p.text),
  null, 2
)
EVALEOF
```

### Step 4: Scroll and extract more (repeat 1-2x for 20+ posts)
```bash
agent-browser --cdp 9222 scroll down 2000
agent-browser --cdp 9222 wait 1500
# repeat eval from Step 3 — adjust .slice(0, 20) to get more
```

## Speed Optimizations

1. **Use `scroll down 2000`** for fast scrolling
2. **Batch extractions** — grab 12-20 posts per eval call
3. **Skip screenshots** — pure text + links extraction is faster
4. **Use 1500ms wait** after scrolling — enough for tweet loading
5. **Use JS eval with data-testid** — more reliable than snapshot text parsing

## Summary Format

Output the summary as readable text:

```
## X Feed Summary

### Main Themes
- Theme 1: description

### Key Highlights
1. **[Post text snippet](https://x.com/user/status/123)** - @user: summary
2. ...

### Viral Content
- High engagement post: [link](url)

### Notable Accounts
- [@handle](https://x.com/handle): active on topics
```

Keep it conversational, scannable, with all links as Markdown [text](url).

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Not logged in | You must use `--cdp 9222`, never `--auto-connect` or a fresh browser |
| `networkidle` timeout | Use `wait 5000` — never use `--load networkidle` on X |
| Feed not loading | Check Chrome is running: `curl -s http://localhost:9222/json/version` |
| Same posts repeating | Scroll further with additional `scroll down 2000` commands |
| No articles found | Page still loading — add another `wait 3000` then retry eval |
| Links missing | Ensure eval captures relative URLs and prepends `https://x.com` |

## X DOM Selectors Reference
- Tweet article: `article[data-testid="tweet"]`
- Tweet text: `[data-testid="tweetText"]`
- User name block: `[data-testid="User-Name"]`
- Timestamp (with href to tweet): `time` inside an `<a>` tag
