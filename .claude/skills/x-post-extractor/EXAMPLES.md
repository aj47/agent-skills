# Examples

Sample extractions showing transcript input → post/thread output.

---

## Example 1: Single Post (Discovery Moment)

### Input Transcript

```
[00:42:15] let's try this cursor alternative, there's so many now dude
[00:42:23] this one's called aide, it's completely free and open source
[00:42:31] let me just... okay here we go
[00:42:45] whoa wait it just autocompleted the entire function
[00:42:52] that's actually really good, and it's running locally
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Tool name + result | "Aide" + "autocompleted entire function" | 5 |
| Discovery moment | "whoa wait" | 2 |
| Value props | "free", "open source", "locally" | - |
| **Total Score** | | **7 (high)** |

### Output

```
---
TYPE: post
PRIORITY: high
SOURCE: 00:42:15 - 00:42:52
TOPIC: Aide (Cursor alternative)
---

POST:
Aide just autocompleted an entire function on first try.

Free. Open source. Runs locally.

Another Cursor alternative worth watching.

Check it out: [link]

---

MEDIA NEEDED:
- Type: screen clip
- Timestamp: 00:42:31 - 00:42:52
- Focus: the autocomplete moment
- Crop notes: show the before (empty function) and after (completed)

---

NOTES:
Strong discovery moment with multiple value props. Good candidate for morning post (tool discovery content). Could expand to thread if comparing to other Cursor alternatives from same stream.
```

### Quality Check

- [x] First 10 words are a hook: "Aide just autocompleted an entire function on first try"
- [x] First word is NOT banned: "Aide" (tool name)
- [x] Tool named in first 50 words: "Aide" in word 1
- [x] Has value prop: "Free. Open source. Runs locally."
- [x] Action CTA: "Check it out: [link]"
- [x] Sentences under 25 words: All sentences <10 words
- [x] Media request specific: Exact timestamps, clear focus

---

## Example 2: Thread (Tool Comparison)

### Input Transcript (Condensed)

```
[00:15:00] alright let's compare these cursor alternatives
[00:15:12] first up is aide, been hearing a lot about this one
...
[00:17:45] dude it just completed that entire auth function
[00:17:52] and this is running completely local, pretty sick
...
[00:20:30] okay next let's try windsurf
[00:20:45] this one has this cascade feature for pair programming
...
[00:22:15] this feels more natural, like working with a human
...
[00:25:00] last one, zed
[00:25:12] this thing opens instantly, no electron bloat
[00:25:30] ai features still catching up but the speed is unreal
...
[00:27:45] so which one would I actually use?
[00:28:00] aide for privacy, windsurf for collaboration, zed for speed
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Multiple tool comparisons | Aide, Windsurf, Zed | 4 |
| Specific results | "completed entire auth function", "opens instantly" | 5 |
| Discovery moments | "dude", "pretty sick", "unreal" | 2 |
| Clear verdict | Tool → use case mapping | 3 |
| **Total Score** | | **14 (high)** |

### Output

```
---
TYPE: thread
PRIORITY: high
SOURCE: 00:15:00 - 00:28:00
TOPIC: AI coding tool comparison
---

THREAD:

1/ Tested 3 Cursor alternatives this week.

One of them is mass sleeping on.

Here's what I found

---

2/ Aide

Free, open source, runs locally.

Autocomplete is surprisingly good—completed entire functions without context.

The local-first approach means your code never leaves your machine.

---

3/ Windsurf

Best for pair programming workflow.

The "Cascade" feature lets you have back-and-forth with the AI naturally.

Feels more like working with a human than a tool.

---

4/ Zed

Blazing fast—opens instantly, no electron.

AI features still catching up but the editor experience is unmatched.

If you value speed over features, this is it.

---

5/ The verdict:

Aide for privacy-first coding.
Windsurf for collaboration.
Zed for raw speed.

All free. All open source. Try them yourself.

---

MEDIA NEEDED:
- Type: before-after screenshots for each tool
- Timestamp: [00:17:30, 00:22:00, 00:25:20]
- Focus: the autocomplete/generation result from each
- Crop notes: consistent framing across all 3 for comparison

---

NOTES:
Comparison threads perform well. Schedule for Tuesday-Thursday morning. Could clip individual tool demos for separate posts later in week.
```

### Quality Check

- [x] Hook compels "Show this thread": Bold claim + curiosity gap
- [x] Each tweet standalone: Yes, each explains one tool
- [x] Max 7 tweets: 5 tweets
- [x] No filler tweets: Every tweet has substance
- [x] Numbered tweets: Using "1/", "2/" format

---

## Example 3: Single Post (Result Statement)

### Input Transcript

```
[01:23:45] let me try this mlx whisper thing
[01:24:02] so it's supposed to be way faster for mac
[01:24:15] running the transcription now...
[01:24:28] wait what
[01:24:32] that was like 3 seconds for a 10 minute video
[01:24:40] dude that's insane, the normal whisper takes like 2 minutes
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Specific metric | "3 seconds for 10 minute video" | 3 |
| Comparison | "normal whisper takes 2 minutes" | 4 |
| Strong reaction | "wait what", "insane" | 2 |
| **Total Score** | | **9 (high)** |

### Output

```
---
TYPE: post
PRIORITY: high
SOURCE: 01:23:45 - 01:24:40
TOPIC: MLX Whisper
---

POST:
MLX Whisper transcribed a 10-minute video in 3 seconds.

Normal Whisper takes 2 minutes for the same file.

40x faster. Free. Runs on Apple Silicon.

If you're on Mac, this is a no-brainer.

---

MEDIA NEEDED:
- Type: terminal output
- Timestamp: 01:24:15 - 01:24:35
- Focus: the terminal showing transcription completion time
- Crop notes: show the timing output clearly

---

NOTES:
Strong metric-driven post. The 40x comparison is compelling. Could pair with a short demo clip. Best for developer audience on Mac.
```

---

## Example 4: Skip Example (Negative Without Resolution)

### Input Transcript

```
[02:15:00] this thing is so frustrating
[02:15:12] why doesn't it just work
[02:15:25] I've tried like 5 different things
[02:15:40] ugh whatever, let's move on to something else
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Frustration | Yes | 0 |
| Resolution | No | 0 |
| Tool result | None | 0 |
| **Total Score** | | **0 (skip)** |

### Decision: SKIP

**Reason**: Negative without resolution. No tool name, no solution, no learning. This would only generate negative content with no value.

---

## Example 5: Skip Example (Off-Topic)

### Input Transcript

```
[00:55:00] so anyway my cat knocked over my coffee this morning
[00:55:12] had to clean up the whole desk
[00:55:25] that's why I was late starting the stream
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Tech/AI content | No | 0 |
| Tool mention | No | 0 |
| Discovery moment | No | 0 |
| **Total Score** | | **0 (skip)** |

### Decision: SKIP

**Reason**: Off-topic personal tangent. No tech content, no tool discovery, no value for followers expecting AI/dev content.

---

## Example 6: Problem → Solution Arc

### Input Transcript

```
[03:45:00] okay I've been stuck on this auth bug for like an hour
[03:45:15] the token keeps expiring before the request finishes
[03:45:30] tried extending the timeout, tried caching, nothing works
...
[03:52:00] wait wait wait
[03:52:12] figured it out
[03:52:25] the refresh was happening DURING the request
[03:52:40] needed to await the refresh before making the call
[03:52:55] boom, works perfectly now
```

### Detection Analysis

| Signal | Found | Score |
|--------|-------|-------|
| Problem → solution arc | Yes | 4 |
| Resolution marker | "figured it out", "boom" | 2 |
| Specific fix | "await the refresh before making the call" | 3 |
| **Total Score** | | **9 (high)** |

### Output

```
---
TYPE: post
PRIORITY: high
SOURCE: 03:45:00 - 03:52:55
TOPIC: Auth token refresh bug
---

POST:
Spent an hour debugging an auth bug.

Token kept expiring mid-request.

The fix: await the token refresh BEFORE making the API call, not during.

One-line change. Works perfectly now.

Save this for when you hit the same issue.

---

MEDIA NEEDED:
- Type: before-after
- Timestamp: 03:52:25 - 03:52:55
- Focus: the code fix
- Crop notes: show the problematic code and the fix side by side

---

NOTES:
Good debugging story. Relatable problem for developers. The "save this" CTA encourages bookmarking. Could work well for weekend posting when devs are doing side projects.
```

---

## Output JSON Example

Complete `x_posts.json` output:

```json
{
  "total_extractions": 4,
  "posts": [
    {
      "type": "post",
      "priority": "high",
      "source": {
        "start_time": "00:42:15",
        "end_time": "00:42:52",
        "start_index": 156,
        "end_index": 162
      },
      "topic": "Aide (Cursor alternative)",
      "content": "Aide just autocompleted an entire function on first try.\n\nFree. Open source. Runs locally.\n\nAnother Cursor alternative worth watching.\n\nCheck it out: [link]",
      "media": {
        "type": "screen clip",
        "timestamp_start": "00:42:31",
        "timestamp_end": "00:42:52",
        "focus": "the autocomplete moment",
        "crop_notes": "show the before (empty function) and after (completed)"
      },
      "notes": "Strong discovery moment with multiple value props.",
      "quality_checks": {
        "hook_in_first_10_words": true,
        "no_banned_first_word": true,
        "tool_in_first_50_words": true,
        "has_value_prop": true,
        "has_action_cta": true,
        "avg_sentence_under_25_words": true,
        "media_request_specific": true
      },
      "score_breakdown": {
        "tool_with_result": 5,
        "comparison": 0,
        "metric": 0,
        "reaction": 2,
        "discovery": 0,
        "total": 7
      }
    },
    {
      "type": "post",
      "priority": "high",
      "source": {
        "start_time": "01:23:45",
        "end_time": "01:24:40",
        "start_index": 412,
        "end_index": 420
      },
      "topic": "MLX Whisper",
      "content": "MLX Whisper transcribed a 10-minute video in 3 seconds.\n\nNormal Whisper takes 2 minutes for the same file.\n\n40x faster. Free. Runs on Apple Silicon.\n\nIf you're on Mac, this is a no-brainer.",
      "media": {
        "type": "terminal output",
        "timestamp_start": "01:24:15",
        "timestamp_end": "01:24:35",
        "focus": "terminal showing transcription completion time",
        "crop_notes": "show timing output clearly"
      },
      "notes": "Strong metric-driven post. The 40x comparison is compelling.",
      "quality_checks": {
        "hook_in_first_10_words": true,
        "no_banned_first_word": true,
        "tool_in_first_50_words": true,
        "has_value_prop": true,
        "has_action_cta": false,
        "avg_sentence_under_25_words": true,
        "media_request_specific": true
      },
      "score_breakdown": {
        "tool_with_result": 0,
        "comparison": 4,
        "metric": 3,
        "reaction": 2,
        "discovery": 0,
        "total": 9
      }
    },
    {
      "type": "post",
      "priority": "high",
      "source": {
        "start_time": "03:45:00",
        "end_time": "03:52:55",
        "start_index": 890,
        "end_index": 915
      },
      "topic": "Auth token refresh bug",
      "content": "Spent an hour debugging an auth bug.\n\nToken kept expiring mid-request.\n\nThe fix: await the token refresh BEFORE making the API call, not during.\n\nOne-line change. Works perfectly now.\n\nSave this for when you hit the same issue.",
      "media": {
        "type": "before-after",
        "timestamp_start": "03:52:25",
        "timestamp_end": "03:52:55",
        "focus": "the code fix",
        "crop_notes": "show problematic code and fix side by side"
      },
      "notes": "Good debugging story. Relatable problem for developers.",
      "quality_checks": {
        "hook_in_first_10_words": true,
        "no_banned_first_word": true,
        "tool_in_first_50_words": false,
        "has_value_prop": false,
        "has_action_cta": true,
        "avg_sentence_under_25_words": true,
        "media_request_specific": true
      },
      "score_breakdown": {
        "tool_with_result": 0,
        "comparison": 0,
        "metric": 0,
        "reaction": 2,
        "discovery": 0,
        "total": 9
      }
    }
  ],
  "threads": [
    {
      "type": "thread",
      "priority": "high",
      "source": {
        "start_time": "00:15:00",
        "end_time": "00:28:00",
        "segments": [
          {"start": "00:15:00", "end": "00:18:00"},
          {"start": "00:20:30", "end": "00:23:00"},
          {"start": "00:25:00", "end": "00:28:00"}
        ]
      },
      "topic": "AI coding tool comparison",
      "tweets": [
        "1/ Tested 3 Cursor alternatives this week.\n\nOne of them is mass sleeping on.\n\nHere's what I found",
        "2/ Aide\n\nFree, open source, runs locally.\n\nAutocomplete is surprisingly good—completed entire functions without context.\n\nThe local-first approach means your code never leaves your machine.",
        "3/ Windsurf\n\nBest for pair programming workflow.\n\nThe \"Cascade\" feature lets you have back-and-forth with the AI naturally.\n\nFeels more like working with a human than a tool.",
        "4/ Zed\n\nBlazing fast—opens instantly, no electron.\n\nAI features still catching up but the editor experience is unmatched.\n\nIf you value speed over features, this is it.",
        "5/ The verdict:\n\nAide for privacy-first coding.\nWindsurf for collaboration.\nZed for raw speed.\n\nAll free. All open source. Try them yourself."
      ],
      "media": {
        "type": "before-after screenshots",
        "timestamps": ["00:17:30", "00:22:00", "00:25:20"],
        "focus": "autocomplete/generation result from each tool",
        "crop_notes": "consistent framing across all 3 for comparison"
      },
      "notes": "Comparison threads perform well. Schedule for Tuesday-Thursday morning.",
      "quality_checks": {
        "hook_tweet_compels_expand": true,
        "each_tweet_standalone": true,
        "max_7_tweets": true,
        "no_filler_tweets": true
      }
    }
  ],
  "metadata": {
    "stream_title": "Testing AI Coding Tools Live",
    "stream_date": "2025-01-15",
    "total_sentences_scanned": 4400,
    "total_duration": "06:42:45",
    "moments_detected": 15,
    "posts_extracted": 3,
    "threads_extracted": 1,
    "skipped": {
      "off_topic": 2,
      "incomplete": 3,
      "negative_no_resolution": 1,
      "duplicate": 1,
      "low_priority": 4
    }
  }
}
```
