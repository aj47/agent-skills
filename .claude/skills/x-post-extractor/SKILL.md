---
name: x-post-extractor
description: Extract high-quality X posts and threads from stream transcripts. Finds shareable moments, discoveries, and insights with media requests.
---

# X Post Extractor Skill

Analyzes stream transcription files to extract high-quality X (Twitter) posts and threads, optimized for engagement using proven voice patterns.

## Quick Start

When you have a stream transcription, ask Claude to extract posts:

```
User: "Extract X posts from my stream"
```

You will automatically:
1. Detect the transcription file and check for `parsed.json`
2. Scan for trigger phrases and score moments
3. Generate posts/threads with media requests
4. Output to `x_posts.json`

## Inputs Required

| Input | Required | Description |
|-------|----------|-------------|
| Stream transcript | Yes | Timestamped transcript (parsed.json or out.json) |
| Stream title/topic | Yes | Context for relevance filtering |
| Stream recording access | Yes | For screenshot/clip extraction |

## Execution Checklist

When user asks to extract X posts, follow this exact sequence:

### Phase 1: Detect & Parse Transcript

- [ ] Check if `parsed.json` exists in current directory
- [ ] If not, look for transcription JSON (`out.json` or `*.json` with `sentences` array)
- [ ] If no parsed file exists, run: `python .claude/skills/clipper/scripts/parse_transcription.py <transcription> > parsed.json`
- [ ] Note the stream title/topic from filename or ask user

### Phase 2: Scan & Score Moments

- [ ] Read `parsed.json` in windows (100-200 sentences at a time)
- [ ] Scan each sentence for trigger phrases (see Detection Logic below)
- [ ] Score matches using the Scoring Priority system
- [ ] Track all detected moments with timestamps
- [ ] Skip moments that are off-topic, incomplete, or negative without resolution

### Phase 3: Generate Posts & Threads

For each high-scoring moment:
- [ ] Determine format: single post vs thread
- [ ] Draft content using Voice Guidelines (see [VOICE.md](VOICE.md))
- [ ] Apply formatting rules (see [FORMATS.md](FORMATS.md))
- [ ] Specify media request with timestamps
- [ ] Run quality checklist
- [ ] Add to output

### Phase 4: Write Output

- [ ] Write `x_posts.json` with all extracted posts/threads
- [ ] Report summary to user (posts found, priority breakdown, topics)

---

## Detection Logic

### Trigger Phrases to Scan

**1. Discovery Moments** (high engagement potential)
- Exclamations: "whoa", "dude", "that's actually", "wait", "sick", "boom"
- Surprise phrases: "I didn't know it could", "I haven't seen this before"
- Appreciation: "that's pretty cool", "that's really cool"

**2. Result Statements** (proof of value)
- Success indicators: "it worked", "it just", "there we go", "here we go"
- Specific metrics: stars, time saved, lines of code, speed, percentages
- Before/after: improvement metrics, comparison numbers

**3. Comparison Signals** (context and positioning)
- Comparators: "better than", "beats", "faster than", "unlike"
- Superlatives: tool name + "best", "fastest", "easiest", "first"
- Alternatives: "instead of", "replaced", "switched from"

**4. Problem→Solution Arcs** (narrative hooks)
- Resolution markers: "finally", "figured it out", "the fix was", "turns out"
- Pattern: frustration followed by resolution within 2-3 minutes of transcript
- Breakthrough moments: "oh that's why", "now it makes sense"

### Scanning Process

When reading the transcript:

1. **First pass**: Flag sentences containing any trigger phrase
2. **Context expansion**: Include 1-2 sentences before and after for context
3. **Timestamp extraction**: Note exact start/end times for media requests
4. **Deduplication**: If same tool/topic appears multiple times, keep the strongest moment

---

## Scoring Priority

Rank each detected moment by presence of these signals (highest to lowest):

| Priority | Signal | Weight | Example |
|----------|--------|--------|---------|
| 1 (Highest) | Tool name + specific result | 5 | "Cursor completed the entire function in 2 seconds" |
| 2 | Comparison to known tool | 4 | "This beats ChatGPT for coding tasks" |
| 3 | Metric or number | 3 | "Went from 500ms to 50ms load time" |
| 4 | Strong reaction word | 2 | "Whoa, that's actually incredible" |
| 5 (Lowest) | General discovery energy | 1 | "This is pretty cool" |

**Priority Mapping:**
- Score 5+: **high** priority
- Score 3-4: **medium** priority
- Score 1-2: **low** priority

---

## Skip Criteria

Do NOT extract moments that are:

- **Off-topic**: Non-AI/tech tangents, personal stories unrelated to tools
- **Incomplete**: Abandoned explorations, interrupted thoughts
- **Negative without resolution**: Complaints without solutions or learnings
- **Duplicate**: Already covered same tool/insight in a previous extraction
- **Too vague**: Generic excitement without specific tool/insight

---

## Format Selection

**Use Single Post when:**
- Discovery is self-contained
- 1-2 key points only
- No multi-step process
- Can be expressed in <280 characters (400 max)

**Use Thread when:**
- 3+ distinct points
- Multi-step process or tutorial
- Comparison of multiple things
- Story arc with beginning/middle/end
- Need more than 400 characters to convey value

---

## Output Format

Create `x_posts.json` with this structure:

```json
{
  "total_extractions": 5,
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
      "notes": "Strong discovery moment with multiple value props. Good candidate for morning post.",
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
        "total": 5
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
        "3/ [Tool 2]\n\n[Key differentiator]\n\n[Specific result or metric]\n\n[One honest limitation]",
        "4/ [Tool 3]\n\n[Key differentiator]\n\n[Specific result or metric]\n\n[One honest limitation]",
        "5/ The verdict:\n\n[Tool X] for [use case].\n[Tool Y] for [use case].\n[Tool Z] if you need [specific thing].\n\nAll free. All open source. Try them yourself."
      ],
      "media": {
        "type": "before-after screenshots",
        "timestamps": ["00:16:30", "00:21:15", "00:26:00"],
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
    "total_duration": "6:42:45",
    "moments_detected": 15,
    "posts_extracted": 3,
    "threads_extracted": 2,
    "skipped": {
      "off_topic": 2,
      "incomplete": 3,
      "duplicate": 1,
      "low_priority": 4
    }
  }
}
```

---

## Quality Checklist

Before finalizing any extraction, verify:

**For Single Posts:**
- [ ] First 10 words are a hook (not context)
- [ ] First word is NOT "so", "hey", "I", "what's up", "just wanted to share"
- [ ] Tool/topic named in first 50 words
- [ ] At least one value prop (free/fast/local/easy) if applicable
- [ ] CTA is action-oriented (not "subscribe" or "follow")
- [ ] Sentences average <25 words
- [ ] Media request is specific and capturable
- [ ] No overlap with recent extractions

**For Threads:**
- [ ] Hook tweet compels "Show this thread" click
- [ ] Each tweet can standalone (assume someone sees it via RT)
- [ ] Max 7 tweets (5 ideal)
- [ ] No filler tweets—every tweet earns its place
- [ ] Tweets numbered or have clear headers
- [ ] Final tweet has actionable CTA

---

## Batch Processing Notes

When processing a full stream:

1. Scan entire transcript first, flag all potential moments
2. Rank by priority score
3. Check for redundancy (don't extract 3 posts about same tool)
4. Aim for 2-4 extractions per 1-hour stream
5. Mix of posts and threads ideal (e.g., 2 posts + 1 thread)
6. Note timestamps that could become TikTok/Shorts clips (add to notes)

---

## Multi-step Analysis Process

Since transcripts can be large, analyze in overlapping windows:

1. **Get total count**: Read `parsed.json` metadata for total sentences
2. **Analyze in windows**: Use 200-sentence windows with 50-sentence overlap
   - Window 1: Sentences 0-200
   - Window 2: Sentences 150-350
   - Window 3: Sentences 300-500
   - Continue until all analyzed
3. **Track all moments**: Keep running list with timestamps and scores
4. **Deduplicate**: Same topic in multiple windows → keep highest scoring
5. **Rank and select**: Sort by score, take top 2-4 per hour of stream
6. **Generate content**: Write posts/threads for selected moments
7. **Write output**: Create `x_posts.json`

---

## Example Analysis Output

```
Scan complete! Analyzed 4400 sentences (6.7 hours).

Moments detected: 15
  - Discovery moments: 6
  - Result statements: 4
  - Comparisons: 3
  - Problem→Solution: 2

After scoring and deduplication:
  - High priority: 3
  - Medium priority: 4
  - Low priority: 3
  - Skipped: 5 (2 off-topic, 2 duplicate, 1 incomplete)

Extracting top moments...

Generated:
  - 3 single posts (2 high, 1 medium priority)
  - 1 thread (high priority, 5 tweets)

Output saved to x_posts.json
```

---

## Supporting Documents

- [VOICE.md](VOICE.md) - Voice guidelines (words to use/avoid)
- [FORMATS.md](FORMATS.md) - Post and thread format templates
- [EXAMPLES.md](EXAMPLES.md) - Sample extractions with inputs/outputs

---

## Integration with Other Skills

This skill works alongside:

- **clipper**: Uses same `parsed.json` input format
- **media-fetcher**: Can fetch media assets based on media requests in output

**Typical workflow:**
```
1. User runs transcription → out.json
2. Run clipper → video clips in clips/
3. Run x-post-extractor → x_posts.json with media requests
4. Run media-fetcher → media assets for posts
5. User publishes posts with media
```

---

## Requirements

- **Python 3.8+** for parse script (uses clipper's script)
- Stream transcription in JSON format with timestamps

---

## Troubleshooting

**"No moments found"**: The stream may lack strong discovery/result moments. Try lowering the score threshold or look for teaching moments instead.

**"Too many moments"**: Increase score threshold to 4+ or be more aggressive with deduplication.

**"Posts feel generic"**: Ensure you're capturing specific tool names and metrics, not just reaction words.
