# Output Formats

Templates and rules for single posts and threads.

---

## Single Post Format

### When to Use

- Discovery is self-contained
- 1-2 key points only
- No multi-step process
- Can express value in <400 characters

### Structure Template

```
[HOOK - first 10 words, bold claim or result]

[VALUE PROPS - free/local/fast/open source if applicable]

[ONE-LINE INSIGHT OR REACTION]

[CTA - try it / check it out / download]
```

### Rules

| Rule | Requirement |
|------|-------------|
| Preferred length | 280 characters |
| Absolute max | 400 characters |
| Line breaks | Between each thought |
| Hashtags | None in body (optional 1-2 at end only) |
| Emojis | None unless quoting chat |
| First word | NOT "so", "hey", "what's up", "just wanted to share" |

### Example

```
Aide just autocompleted an entire function on first try.

Free. Open source. Runs locally.

Another Cursor alternative worth watching.

Check it out: [link]
```

**Character count**: 156 characters

---

## Thread Format

### When to Use

- 3+ distinct points
- Multi-step process or tutorial
- Comparison of multiple things
- Story arc with beginning/middle/end
- Need >400 characters to convey value

### Structure Template

**Tweet 1 (Hook):**
```
[BOLD CLAIM OR RESULT]

[CURIOSITY GAP - what they'll learn]

[THREAD INDICATOR - optional single emoji or word]
```

**Tweets 2-5 (Value):**
```
[NUMBER]. [POINT HEADER]

[1-2 sentences explaining]

[Optional: specific example or metric]
```

**Final Tweet (CTA):**
```
[RECAP - one sentence summary]

[ACTION CTA - try it / link / check it out]

[Optional: "Follow for more [topic]" - use sparingly]
```

### Rules

| Rule | Requirement |
|------|-------------|
| Max tweets | 7 (5 ideal) |
| Min tweets | 3 |
| Each tweet | Must standalone (assume RT visibility) |
| Numbering | Use "1/", "2/" etc. OR headers |
| Hook tweet | Must compel "Show this thread" click |
| Filler tweets | None—every tweet earns its place |

### Example

```
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

All free. All worth trying.

Links in reply.
```

---

## Media Request Format

Every extraction must include a media specification:

```
MEDIA NEEDED:
- Type: [screenshot/clip/terminal/before-after]
- Timestamp: [HH:MM:SS - HH:MM:SS]
- Focus: [what specifically to capture]
- Crop notes: [what to highlight or exclude]
```

### Media Types

| Type | When to Use | Format |
|------|-------------|--------|
| **Screenshot** | UI result, output, code snippet | PNG, highlight key area |
| **Screen clip** | Demo moment, before/after | <60 sec, MP4 |
| **Terminal output** | CLI tools, build results | Screenshot or text block |
| **Before/after** | Transformations, improvements | Side-by-side or sequential |

### Text-Only Flag

If moment is purely verbal with no visual:

```
MEDIA: Text-only viable (no visual demo)
PRIORITY: Lower - consider skipping unless insight is exceptional
```

**Note**: Text-only posts should be exceptional. Prefer moments with demonstrable visuals.

---

## JSON Output Schema

### Single Post Object

```json
{
  "type": "post",
  "priority": "high|medium|low",
  "source": {
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS",
    "start_index": 0,
    "end_index": 0
  },
  "topic": "Tool or concept name",
  "content": "Full post text with line breaks",
  "media": {
    "type": "screenshot|clip|terminal|before-after",
    "timestamp_start": "HH:MM:SS",
    "timestamp_end": "HH:MM:SS",
    "focus": "What to capture",
    "crop_notes": "What to highlight or exclude"
  },
  "notes": "Context for review - timing suggestions, related posts",
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
    "tool_with_result": 0,
    "comparison": 0,
    "metric": 0,
    "reaction": 0,
    "discovery": 0,
    "total": 0
  }
}
```

### Thread Object

```json
{
  "type": "thread",
  "priority": "high|medium|low",
  "source": {
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS",
    "segments": [
      {"start": "HH:MM:SS", "end": "HH:MM:SS"}
    ]
  },
  "topic": "Thread topic",
  "tweets": [
    "1/ Hook tweet text",
    "2/ Value tweet 1",
    "3/ Value tweet 2",
    "4/ CTA tweet"
  ],
  "media": {
    "type": "screenshot|clip|before-after",
    "timestamps": ["HH:MM:SS", "HH:MM:SS"],
    "focus": "What to capture",
    "crop_notes": "Consistency notes for multi-image"
  },
  "notes": "Scheduling suggestions, related content notes",
  "quality_checks": {
    "hook_tweet_compels_expand": true,
    "each_tweet_standalone": true,
    "max_7_tweets": true,
    "no_filler_tweets": true
  }
}
```

---

## Character Counting

For accurate character counts:

- Line breaks count as 1 character
- URLs count as 23 characters (t.co shortening)
- Spaces count as 1 character

**Quick reference:**
- 280 chars = ~40-50 words
- 400 chars = ~55-70 words
- Thread tweet = aim for 200-250 chars each

---

## Format Selection Flowchart

```
Is the insight self-contained?
├── Yes → Can you express it in <280 chars?
│         ├── Yes → SINGLE POST (short)
│         └── No → Can you express it in <400 chars?
│                  ├── Yes → SINGLE POST (long)
│                  └── No → THREAD
└── No → Does it have 3+ distinct points?
         ├── Yes → THREAD
         └── No → Consider splitting or expanding to thread
```
