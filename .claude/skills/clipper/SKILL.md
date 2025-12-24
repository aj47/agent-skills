---
name: clipper
description: Analyze video transcriptions to identify interesting segments for clipping. Finds highlights, key moments, and reactions with precise timestamps. Use when working with video transcriptions to extract clip-worthy moments.
---

# Video Clipper Skill

Analyzes video transcription files to identify the most interesting and clip-worthy segments with precise timestamps.

## Quick Start

To find interesting clips in a video transcription:

```bash
# 1. Parse the transcription JSON
python .claude/skills/clipper/scripts/parse_transcription.py <transcription.json> > parsed.json

# 2. Ask Claude to analyze the parsed transcription
# Claude will analyze it directly and create segments.json
```

## Workflow

### Step 1: Parse Transcription

First, parse the raw transcription to extract sentences with timestamps:

```bash
python .claude/skills/clipper/scripts/parse_transcription.py out.json > parsed.json
```

**Input format**: JSON with `sentences` array containing:
- `text`: Sentence content
- `start`: Start timestamp (seconds)
- `end`: End timestamp (seconds)
- `words`: Array of word-level timestamps

**Output format**: Simplified JSON array of sentences with timestamps

### Step 2: Analyze for Interesting Segments

YOU (Claude) will analyze the parsed transcription directly. Follow this process:

#### Analysis Process

1. **Read the parsed transcription** using the Read tool
2. **Analyze in windows** of approximately 100 sentences at a time to manage context
3. **Identify clip-worthy segments** based on the criteria below
4. **Output structured JSON** with all identified segments

#### Output Format

Create a file called `segments.json` with this structure:

```json
{
  "total_clips": 5,
  "clips": [
    {
      "start_index": 3,
      "end_index": 5,
      "start_time": 18.80,
      "end_time": 26.08,
      "duration": 7.28,
      "text": "Oh my god, that's incredible. Didn't know I could stream like that.",
      "reason": "High-energy reaction to discovering new streaming capability - genuine surprise moment",
      "category": "reaction",
      "confidence": 0.92,
      "suggested_title": "TikTok Vertical Streaming Discovery",
      "key_quote": "Oh my god, that's incredible."
    }
  ],
  "metadata": {
    "total_sentences_analyzed": 4400,
    "total_duration": 24165.0,
    "min_clip_length": 10,
    "max_clip_length": 60,
    "confidence_threshold": 0.6
  }
}
```

#### Analysis Instructions

When analyzing the transcription, identify segments that match these criteria:

**1. High-Energy Moments** (category: "reaction")
- Strong emotional reactions (excitement, surprise, shock, frustration)
- Exclamations and emphatic language
- Sudden tone changes
- Examples: "Oh my god!", "That's incredible!", "No way!"
- **Confidence**: 0.8+ for strong reactions, 0.6-0.7 for moderate

**2. Valuable Tips & Advice** (category: "tip")
- Concrete recommendations with specific tools/methods
- Actionable advice viewers can apply
- "I recommend...", "You should...", "The best way..."
- Examples: "I recommend getting MLX models"
- **Confidence**: 0.8+ for specific tips, 0.6-0.7 for general advice

**3. Teaching Moments** (category: "teaching")
- Technical explanations of concepts
- How things work or why they matter
- Problem-solving demonstrations
- "The way this works...", "The reason is..."
- **Confidence**: 0.7+ for clear explanations, 0.6+ for partial

**4. Questions & Engagement** (category: "question")
- Direct audience interaction
- Rhetorical or direct questions to viewers
- Calls to action
- "What do you think?", "Let me know..."
- **Confidence**: 0.7+ for direct engagement, 0.6+ for rhetorical

**5. Humor & Entertainment** (category: "humor")
- Jokes with setup and punchline
- Funny observations or situations
- Self-deprecating humor
- Relatable moments
- **Confidence**: 0.8+ for clear jokes, 0.6-0.7 for mild humor

**6. Stories & Narratives** (category: "story")
- Personal anecdotes with beginning/middle/end
- Case studies or examples
- "So this one time...", "I remember when..."
- **Confidence**: 0.8+ for complete stories, 0.6-0.7 for brief anecdotes

**7. Strong Opinions** (category: "opinion")
- Controversial or counter-intuitive statements
- Definitive positions on topics
- "I honestly think...", "The truth is..."
- **Confidence**: 0.8+ for strong takes, 0.6-0.7 for mild opinions

#### Technical Requirements for Clips

- **Duration**: Between 10-60 seconds (ideal: 15-45 seconds)
- **Completeness**: Must be complete thoughts, not cut mid-sentence
- **Self-contained**: Understandable without prior video context
- **Natural boundaries**: Start/end at logical points in speech
- **Confidence threshold**: Only include segments with confidence ≥ 0.6

#### Multi-step Process

Since the parsed transcription may be large, analyze it in steps:

1. **Get total count**: Read the parsed.json metadata to see total sentences
2. **Analyze in windows**: Read sentences 0-100, then 100-200, etc.
3. **Track all segments**: Keep a running list of all identified clips
4. **Merge overlapping**: If clips overlap or are very close (within 5 seconds), keep the higher confidence one
5. **Sort by confidence**: Final output should be sorted by confidence score (highest first)
6. **Write output**: Create segments.json with all results

#### Example Analysis Command Flow

```bash
# User runs:
python .claude/skills/clipper/scripts/parse_transcription.py video.json > parsed.json

# Then user asks Claude:
"Analyze parsed.json and find interesting clips"

# Claude then:
# 1. Reads parsed.json to understand structure
# 2. Analyzes sentences in windows
# 3. Identifies all clip-worthy segments
# 4. Writes segments.json with results
# 5. Reports summary to user
```

### Step 3: Review and Export

After analysis, review `segments.json`:
- Clips are sorted by confidence (highest first)
- Each includes precise timestamps for video extraction
- Category and reason explain why it's interesting
- Suggested title for the clip

## What Makes a Good Clip?

See the criteria in Step 2 above, or review [SEGMENT_TYPES.md](SEGMENT_TYPES.md) for detailed guidance on each category.

## Configuration

You can adjust these parameters when analyzing:

- **MIN_CLIP_LENGTH**: 10 seconds (skip shorter segments)
- **MAX_CLIP_LENGTH**: 60 seconds (skip longer segments)
- **CONFIDENCE_THRESHOLD**: 0.6 (only include clips above this score)
- **WINDOW_SIZE**: 100 sentences per analysis window

## Examples

See [EXAMPLES.md](EXAMPLES.md) for sample analyses and outputs.

## Requirements

Python 3.8+ for the parsing script (no additional packages needed for parsing).

## Troubleshooting

**"No segments found"**: The content may be low-energy or monotone. Try lowering confidence threshold mentally to 0.5 or including shorter clips (down to 8 seconds).

**"Too many segments"**: Raise confidence threshold to 0.75+ or increase minimum length to 15-20 seconds.

**Large files**: For very long videos (4+ hours), analyze in smaller windows and take breaks to avoid context limits.
