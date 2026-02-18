---
name: x-post-tweet
description: "Posts tweets to X (Twitter) in AJ's voice. Use when asked to write a tweet, post to Twitter/X, compose a tweet, or share something on X. Handles both writing the tweet copy and posting it via browser automation."
---

# X Tweet Composer & Poster

## Overview
Writes tweets in AJ's voice and posts them to X via the logged-in Chrome session using agent-browser CDP. Combines voice guide, content strategy, and browser automation into one workflow.

## Prerequisites

Requires **chrome-debug-session** skill to be running first. Verify:
```bash
curl -s --max-time 3 http://localhost:9222/json/version
```

---

## AJ's Voice Guide
<!-- VOICE_START -->
# AJ's Voice Guide — Source of Truth
# Edit this file to update your voice everywhere.
# Run: update-voice to sync all skills and Claude projects.
# Last updated: 2025-07-01

## Who You Are
Builder, streamer, AI tools creator. You're the peer who's slightly ahead, showing what's possible with genuine excitement. Not performing — discovering. Not reviewing — building. Every post feels like you just came back from the workshop with something cool to show.

## Core Voice Principles

### Lead with discovery, not commentary
Best format: **what you found → what surprised you → why it matters**
You're not a pundit — you're a builder sharing what you just saw work.

### First words are everything
- Bold claims: 80% success rate
- Questions: 29% success rate
- Start with the result or the surprising thing
- Never start with "so," "hey," or throat-clearing
- Name the tool or specific metric immediately

### Write like you talk on your best days
Power words: **just, actually, dude, pretty cool, boom, free, open source**
Cut: "I think," "kind of," "maybe" — assertive beats hedging every time

### Format for scroll speed
- One idea per line
- Whitespace between thoughts
- Cut every word that isn't earning its place
- 70-100 characters per line for quick-read posts

### End with action, not asks
"Download it" and "try it" → 8x more views than "subscribe" or "follow"
Give people something to do.

## Content Formats

### Discovery post
"just [action] and [surprising result]" → details → "go try it"

### Tool milestone
"[tool] just hit [metric]" → what it does → "download it"

### Feed summary
"just spent X mins reading [source] so you don't have to" → bullets → "go build something"

### Tutorial teaser
"[thing] actually works" → one-line proof → "here's how"

## Tweet Template
```
[surprising result or discovery — bold, specific]

[one supporting detail per line]
[another detail]
[the "why it matters" line]

[action: go try it / download it / go build something]
```

## Real Example (posted tweet)
```
just spent 10 mins reading twitter so you don't have to

robots doing kung fu nunchucks in China — a year ago they couldn't wave

OpenClaw skill ecosystem blowing up

aitmpl.com hit 100k npm downloads

physical intelligence is the next frontier

go build something
```

## What To Avoid
- "I think" / "kind of" / "maybe"
- Starting with "So," "Hey," "Just wanted to share"
- Asking people to subscribe / follow as the CTA
- Passive voice
- Jargon without explanation
- Walls of text without whitespace

<!-- VOICE_END -->

## Tweet Writing Template

```
[surprising result or discovery — bold, specific]

[one supporting detail per line]
[another detail]
[the "why it matters" line]

[action: go try it / download it / go build something]
```

---

## Browser Automation Workflow

### Step 1: Navigate to X home
```bash
agent-browser --cdp 9222 open https://x.com/home
agent-browser --cdp 9222 wait 4000
```
**IMPORTANT: Do NOT use `--auto-connect` for X** — always use `--cdp 9222` to connect to the logged-in Chrome session.

### Step 2: Snapshot to find compose box
```bash
agent-browser --cdp 9222 snapshot -i
```
Look for `textbox "Post text"` — its ref changes every time so **always re-snapshot to get current refs**.

### Step 3: Click the compose textbox
```bash
agent-browser --cdp 9222 click e28  # use actual ref from snapshot
```

### Step 4: Type the tweet
Use `type` (not `fill`) to avoid clearing any existing content:
```bash
agent-browser --cdp 9222 type e28 "your tweet text here"
```
Newlines work fine in the string — X renders them as line breaks in the tweet.

### Step 5: Re-snapshot to get fresh refs + verify Post button is enabled
```bash
agent-browser --cdp 9222 snapshot -i
```
After typing, refs change again. Find the `button "Post"` ref. If it shows `[disabled]`, the text box may be empty — try clicking the textbox again and retyping.

### Step 6: Take a screenshot to visually verify
```bash
agent-browser --cdp 9222 screenshot /tmp/tweet-preview.png
open /tmp/tweet-preview.png
```

### Step 7: Click Post
```bash
agent-browser --cdp 9222 click e47  # use actual Post button ref from latest snapshot
```

### Step 8: Verify it posted
```bash
agent-browser --cdp 9222 wait 3000
agent-browser --cdp 9222 snapshot -i 2>&1 | head -60
```
Success indicator: your tweet appears at the top of the feed with timestamp "Now" and your handle `@techfrenAJ`. The compose box resets to empty and `button "Post"` returns to `[disabled]`.

---

## agent-browser Quirks on X (Key Learnings)

| Issue | Cause | Fix |
|-------|-------|-----|
| `get text @ref` times out | Refs are invalidated after DOM changes | Always re-snapshot before reading |
| `--auto-connect` not logged in | Opens fresh browser, not your Chrome session | Always use `--cdp 9222` |
| `networkidle` times out | X never reaches networkidle state | Use `wait 4000` (fixed ms) instead |
| `get text body` returns JS bundle | X injects massive JS into body | Use JS eval with `data-testid` or snapshot approach |
| Post button stays `[disabled]` | Text didn't land in compose box | Re-click the textbox, re-snapshot, retype |
| Refs like `e28` become stale | Snapshot refs expire on DOM change | Re-snapshot after every click/navigation |
| Link card preview appears | X auto-fetches URL cards | This is fine, doesn't affect posting |

---

## DOM Selectors Reference (for JS eval fallback)
```javascript
// Compose textarea
document.querySelector('[data-testid="tweetTextarea_0"]')

// Post button
document.querySelector('[data-testid="tweetButtonInline"]')

// Verify tweet posted (appears at top of timeline)
document.querySelector('article[data-testid="tweet"]')
```

---

## Content Ideas by Type

**Tech discovery post**: "just [action] and [surprising result]" → details → "go try it"
**Tool milestone**: "[tool] just hit [metric]" → what it does → "download it"
**Feed summary**: "just spent X mins reading [source] so you don't have to" → bullets → "go build something"
**Tutorial teaser**: "[thing] actually works" → one-line proof → "here's how"

---

## Related Skills
- **chrome-debug-session** — Launch Chrome with CDP debugging
- **x-feed-scraper** — Scrape X feed for content to tweet about
- **x-feed-summarizer** — Summarize feed into note (source material for tweet content)
