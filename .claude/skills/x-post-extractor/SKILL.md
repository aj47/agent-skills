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
3. Generate posts/threads
4. Fetch media (screenshots, video clips, logos)
5. Output to `x_posts_output/` folder with copy-paste ready files

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

### Phase 4: Fetch Media (Automatic)

For each post, automatically fetch the required media:

- [ ] Create output directory: `mkdir -p x_posts_output`
- [ ] **Screenshots**: For any URLs mentioned (tools, websites):
  ```bash
  python .claude/skills/media-fetcher/scripts/capture_screenshot.py "<url>" --output x_posts_output/
  ```
- [ ] **Video clips**: Extract from stream recording using ffmpeg:
  ```bash
  ffmpeg -y -ss <start_time> -i "<video_file>" -t <duration> -c:v libx264 -c:a aac -preset fast x_posts_output/<post_number>_<topic>_clip.mp4
  ```
- [ ] **Logos**: For companies/products mentioned:
  ```bash
  python .claude/skills/media-fetcher/scripts/fetch_logos.py "<domain>" --output x_posts_output/
  ```

### Phase 5: Write Output (Copy-Paste Ready)

Create `x_posts_output/` folder with:

- [ ] **Individual text files**: One `.txt` file per post with plain text (no escape characters)
  - Format: `01_topic_name.txt`, `02_topic_name.txt`, etc.
  - Content: Ready to copy-paste directly to Twitter
- [ ] **README.md**: Summary with all posts in code blocks for easy copying
- [ ] **Media files**: Screenshots, clips, and logos named to match posts
- [ ] Report summary to user

**Output Structure:**
```
x_posts_output/
├── README.md                    # All posts with copy-paste blocks
├── 01_topic_name.txt           # Post 1 text
├── 01_topic_name_clip.mp4      # Post 1 video clip
├── screenshot_or_logo.png      # Post 1 image
├── 02_topic_name.txt           # Post 2 text
├── 02_topic_name_clip.mp4      # Post 2 video clip
└── ...
```

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

Create `x_posts_output/` folder with copy-paste ready files:

### Individual Post Files (`.txt`)

Each post gets its own text file with plain text ready to copy:

**`01_aide_cursor_alternative.txt`:**
```
Aide just autocompleted an entire function on first try.

Free. Open source. Runs locally.

Another Cursor alternative worth watching.

Check it out: [link]
```

### README.md Summary

The README contains all posts in code blocks for quick copying:

```markdown
# X Posts - [Stream Title]

## Post 1: Aide (HIGH PRIORITY)

**Copy this:**
\```
Aide just autocompleted an entire function on first try.

Free. Open source. Runs locally.

Another Cursor alternative worth watching.

Check it out: [link]
\```

**Media:**
- Video clip: `01_aide_clip.mp4`
- Screenshot: `aide.com.png`

---

## Post 2: [Next Topic]
...
```

### Thread Files

For threads, create a single file with all tweets separated by `---`:

**`02_cursor_alternatives_thread.txt`:**
```
1/ Tested 3 Cursor alternatives this week.

One of them is mass sleeping on.

Here's what I found

---

2/ Aide

Free, open source, runs locally.

Autocomplete is surprisingly good—completed entire functions without context.

---

3/ [Next tweet]
...
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
7. **Fetch media**: Capture screenshots, extract video clips, fetch logos
8. **Write output**: Create `x_posts_output/` with text files, media, and README

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
  - Medium priority: 1
  - Skipped: 11 (off-topic, duplicate, incomplete)

Generating posts and fetching media...

Fetching media:
  ✓ Screenshot: year-in-code.com.png
  ✓ Screenshot: openrouter.ai.png
  ✓ Logo: xiaomi_com.png
  ✓ Video clip: 01_github_wrapped_clip.mp4 (15s)
  ✓ Video clip: 02_open_router_clip.mp4 (35s)
  ✓ Video clip: 03_playwright_mcp_clip.mp4 (25s)

Output saved to x_posts_output/:
  - 4 text files (copy-paste ready)
  - 3 video clips
  - 3 images (screenshots + logos)
  - README.md with summary
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
- **media-fetcher**: Scripts are called automatically to fetch screenshots and logos

**Typical workflow:**
```
1. User runs transcription → out.json
2. Run x-post-extractor → x_posts_output/ with:
   - Copy-paste ready text files
   - Video clips extracted from stream
   - Screenshots captured automatically
   - Logos fetched for mentioned companies
3. User copies text, attaches media, posts to Twitter
```

**What gets fetched automatically:**
- Screenshots of product/tool websites mentioned
- Video clips from stream at relevant timestamps
- Company logos for brands discussed

---

## Requirements

- **Python 3.8+** for parse script and media-fetcher scripts
- **ffmpeg** for extracting video clips (`brew install ffmpeg`)
- **Playwright** for screenshots (`pip install playwright && playwright install chromium`)
- Stream transcription in JSON format with timestamps
- Stream video file (`.mp4`, `.webm`, `.mkv`) for clip extraction

---

## Troubleshooting

**"No moments found"**: The stream may lack strong discovery/result moments. Try lowering the score threshold or look for teaching moments instead.

**"Too many moments"**: Increase score threshold to 4+ or be more aggressive with deduplication.

**"Posts feel generic"**: Ensure you're capturing specific tool names and metrics, not just reaction words.
