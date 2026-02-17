---
name: x-feed-scraper
description: "Scrapes the X (Twitter) following feed and returns post summaries with links. Use when asked to summarize X feed, check Twitter, read tweets, or get latest posts from people you follow."
---

# X Feed Scraper

## Overview
Scrapes the X.com following tab and returns a human-readable summary of posts with direct links. X uses heavy JavaScript rendering so the page must be scraped via the text content, NOT via `get text body` (which returns raw HTML/JS). The snapshot approach gives clean semantic elements.

## Key Learnings (from real usage)

### DO NOT use `agent-browser get text body`
X injects massive JS bundles into the page body. The actual tweet text is buried but extractable — however it's mixed with thousands of lines of config JSON. Use the structured snapshot + inner text approach instead.

### Page Load Strategy
X never reaches `networkidle` state. Always use a fixed wait instead:
```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 5000
```
Do NOT use `--load networkidle` — it will timeout every time.

### Chrome Remote Debugging
X requires a logged-in Chrome session. Always use `--cdp 9222` to connect to the existing Chrome instance (user's logged-in profile).

Check Chrome is running first:
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```

If Chrome is not running on port 9222, launch it:
```bash
open -a "Google Chrome" --args --remote-debugging-port=9222 --profile-directory=Default
sleep 3
```

## Workflow

### Step 1: Verify Chrome is running
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```
If no response, launch Chrome with debugging enabled (see above).

### Step 2: Navigate to Following feed
```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 5000
```

### Step 3: Click "Following" tab to ensure correct feed
After snapshot, look for the Following tab ref and click it:
```bash
agent-browser --cdp 9222 snapshot -i
# find the "Following" tab ref, e.g. e20
agent-browser --cdp 9222 click e20
agent-browser --cdp 9222 wait 3000
```

### Step 4: Extract post data using JavaScript evaluation
Use JS eval to extract structured tweet data — this is the most reliable method:

```bash
agent-browser --cdp 9222 eval "
  const articles = document.querySelectorAll('article[data-testid=\"tweet\"]');
  const posts = [];
  articles.forEach(a => {
    const userEl = a.querySelector('[data-testid=\"User-Name\"]');
    const textEl = a.querySelector('[data-testid=\"tweetText\"]');
    const timeEl = a.querySelector('time');
    const linkEl = timeEl ? timeEl.closest('a') : null;
    const statsEls = a.querySelectorAll('[data-testid$=\"count\"]');
    
    const user = userEl ? userEl.innerText.replace(/\n/g, ' ') : 'Unknown';
    const text = textEl ? textEl.innerText : '';
    const time = timeEl ? timeEl.getAttribute('datetime') : '';
    const href = linkEl ? linkEl.getAttribute('href') : '';
    const link = href ? 'https://x.com' + href : '';
    
    if (text) posts.push({ user, text, time, link });
  });
  JSON.stringify(posts, null, 2);
"
```

### Step 5: Scroll for more posts (optional)
```bash
agent-browser --cdp 9222 scroll 0 800
agent-browser --cdp 9222 wait 2000
# repeat eval
```

### Step 6: Format the summary
Present each post as:
- **@handle** (time ago): post text — [link](https://x.com/...)

## Fallback: Snapshot-based extraction
If JS eval fails, use snapshot to get element refs, then extract text from tweet elements:

```bash
agent-browser --cdp 9222 snapshot -i
```

From the snapshot, tweet authors appear as link refs (e.g. `link "Ray Fernando Verified account"`), tweet text as link refs containing the post content, and time as link refs like `link "6 hours ago"`.

To get tweet URL from a time element ref:
```bash
agent-browser --cdp 9222 get attribute e44 href
```

This returns the relative path like `/RayFernando1337/status/123456789` — prepend `https://x.com` to get the full link.

## Template Output Format

```
Here's your X following feed:

1. **Ray Fernando** (@RayFernando1337) · 6h
   Making OpenClaw Actually Remember Things
   https://x.com/RayFernando1337/status/...

2. **Dorian Develops** (@DorianDevelops) · 7h  
   Who decided K8 was a good nickname for Kubernetes?
   https://x.com/DorianDevelops/status/...
```

## Common Issues

| Problem | Solution |
|---------|----------|
| `networkidle` timeout | Use `wait 5000` instead, never use `--load networkidle` on X |
| `get text body` returns JS bundle | Use JS eval with `data-testid` selectors instead |
| Chrome not connected | Launch Chrome with `--remote-debugging-port=9222` |
| No tweets visible | Click "Following" tab explicitly; feed may default to "For You" |
| Eval returns empty array | Wait longer (8000ms) or scroll down first; React may not have rendered |

## X DOM Selectors Reference
- Tweet article: `article[data-testid="tweet"]`
- Tweet text: `[data-testid="tweetText"]`
- User name block: `[data-testid="User-Name"]`
- Timestamp (with href to tweet): `time` inside an `<a>` tag
- Retweet label: `[data-testid="socialContext"]`
- Like count: `[data-testid="like"] span`
