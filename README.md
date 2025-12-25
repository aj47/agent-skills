# Video Clipper Skill

A Claude Code skill for analyzing video transcriptions and automatically identifying the most interesting and clip-worthy segments.

## Quick Start

**All you need:** Your transcription JSON file (e.g., `out.json`) and video file in the same directory.

Simply ask Claude:
```
"Find interesting clips from my video"
```

Claude will automatically:
1. ✅ Parse your transcription (if needed)
2. ✅ Analyze it to find clip-worthy moments
3. ✅ Create `segments.json` with all clips and metadata
4. ✅ Ask if you want to extract the clips
5. ✅ Extract all clips with word-level precision

**No API setup needed!** Claude Code handles everything - no extra API keys or costs.

Automatically extracts all clips with:
- **Word-level precision** - Uses exact word timestamps, not sentence timestamps
- **0.1s safety buffer** - Prevents clipping inside words
- **Filler word removal** - Strips out "um", "uh", "ah", "like", etc.
- **Silence removal** - Removes gaps > 0.4s between words
- **Clip combining** - Merges multi-part segments into single polished videos
- **Length constraints** - Only creates clips between 1 minute and 6 minutes for better context
- **High quality** - Re-encodes with H.264 for perfect timing

## What It Does

The skill analyzes video transcriptions to identify:

- **High-energy moments**: Reactions, excitement, surprise
- **Valuable content**: Tips, advice, teaching moments
- **Engagement**: Questions, audience interaction
- **Entertainment**: Humor, stories, relatable moments
- **Strong opinions**: Hot takes, controversial statements

Each identified segment includes:
- Precise start/end timestamps
- Category and reason for selection
- Confidence score (0.0-1.0)
- Suggested clip title
- Key quote

## How It Works

### Fully Automatic Workflow

When you ask Claude to find clips from your video, it automatically:

**Step 1: Parse Transcription** (if needed)
- Detects your transcription file (usually `out.json`)
- Runs `parse_transcription.py` to create a simplified version
- Caches result as `parsed.json` for faster future analysis

**Step 2: Analyze for Clip-Worthy Moments**
Claude reads the parsed transcription and:
1. Analyzes sentences in manageable windows
2. Identifies clip-worthy moments based on 7 categories
3. Assigns confidence scores
4. Creates `segments.json` with all results

**Why this approach?**
- ✅ No API costs - uses Claude Code itself
- ✅ No API key setup required
- ✅ Better integration with your workflow
- ✅ Same high-quality analysis from Claude Sonnet 4.5

**Step 3: Extract Video Clips** (optional)
Claude asks if you want clips extracted, then automatically:
- Detects your video file (looks for `*.mp4`, `*.mov`, etc.)
- Runs `extract_clips.py` with the right parameters
- Extracts all clips to `clips/` directory

**Features:**
- Uses word-level timestamps for frame-perfect accuracy
- Adds 0.1s buffer before/after to avoid clipping mid-word
- Removes filler words (um, uh, ah, like, etc.) automatically
- Automatically detects and removes silences > 0.4s
- Combines multi-part segments into single polished clips
- Enforces 1 minute minimum and 6 minute maximum length for better context
- Re-encodes with ffmpeg for precise timing

**Output:**
- `clips/001_TikTok_Vertical_Streaming_Discovery.mp4`
- `clips/002_Why_I_Stopped_Using_Local_LLMs.mp4`
- etc...

## Transcription Format

The skill expects a JSON file with this structure:

```json
{
  "text": "Full transcript...",
  "sentences": [
    {
      "text": "Sentence text",
      "start": 2.56,
      "end": 3.68,
      "duration": 1.12,
      "words": [...]
    }
  ]
}
```

## Example Output

After Claude analyzes your transcription, `segments.json` will contain:

```json
{
  "total_clips": 15,
  "clips": [
    {
      "start_index": 3,
      "end_index": 5,
      "start_time": 18.80,
      "end_time": 26.08,
      "duration": 7.28,
      "text": "Oh my god, that's incredible. Didn't know I could stream like that.",
      "reason": "High-energy reaction to discovering new streaming capability",
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

## Clip Categories

1. **reaction** - High-energy emotional moments
2. **tip** - Actionable advice and recommendations
3. **teaching** - Educational explanations
4. **question** - Audience engagement and interaction
5. **humor** - Jokes and entertaining moments
6. **story** - Personal anecdotes and narratives
7. **opinion** - Strong takes and controversial statements

## Configuration

When you ask Claude to analyze, you can specify parameters:

- **Minimum length**: "Find clips at least 15 seconds long"
- **Maximum length**: "Only clips under 45 seconds"
- **Confidence threshold**: "Only high-confidence clips above 0.75"
- **Specific categories**: "Find only tips and teaching moments"

## Extracting Video Clips

The `extract_clips.py` script automatically extracts all clips with advanced features:

```bash
python .claude/skills/clipper/scripts/extract_clips.py segments.json out.json "Morning+Chillin.mp4" clips/
```

### Word-Level Precision

Instead of using sentence-level timestamps, the script:
1. Loads word-level timestamps from the original transcription
2. Finds the exact first and last words of each segment
3. Adds a 0.1s safety buffer before/after to prevent clipping mid-word
4. Results in frame-perfect clip boundaries

### Filler Word & Silence Removal

The script automatically cleans up clips:
- **Filler words**: Removes "um", "uh", "ah", "like", "er", "hmm", etc.
- **Silences**: Scans all word gaps within each segment
- **Gap detection**: Identifies silences > 0.4s duration
- **Combining**: Removes silences and combines remaining parts into one clip

**Example:** A 45-second segment with filler words and 2-second silence:
1. Removes filler words
2. Splits at silence into 2 parts (20s + 23s of talking)
3. Combines into: `001_Clip_Title.mp4` (single 43s file, no dead air)

### Configuration

Edit `scripts/extract_clips.py` to adjust:

```python
SAFETY_BUFFER = 0.1       # Buffer before/after words (seconds)
SILENCE_THRESHOLD = 0.4   # Min gap to consider silence (seconds)
MIN_CLIP_LENGTH = 60.0    # Minimum total clip length (1 minute)
MAX_CLIP_LENGTH = 360.0   # Maximum total clip length (6 minutes)
MIN_SUBCLIP_LENGTH = 3.0  # Min length for sub-clip segments (seconds)
FILLER_WORDS = {...}      # Set of filler words to remove
```

### Manual Extraction (Alternative)

If you prefer manual control, use ffmpeg directly:

```bash
ffmpeg -i "video.mp4" -ss 18.8 -to 26.08 -c:v libx264 -c:a aac output.mp4
```

## Using with Claude Code

This is a Claude Code skill - it activates automatically when you work with video transcriptions.

**Example prompts:**
- "Find interesting clips from my video"
- "What are the best moments to clip from this video?"
- "Analyze my transcription and extract the top 15 clips"
- "Find high-energy reactions and teaching moments"
- "Show me only tip segments with high confidence"
- "Find longer clips around 2-3 minutes for YouTube"

Claude will automatically detect your transcription and video files, handle all the processing, and ask if you want clips extracted.

## Documentation

- **[SKILL.md](.claude/skills/clipper/SKILL.md)**: Complete skill documentation with analysis instructions
- **[SEGMENT_TYPES.md](.claude/skills/clipper/SEGMENT_TYPES.md)**: Detailed criteria for each clip category
- **[EXAMPLES.md](.claude/skills/clipper/EXAMPLES.md)**: Usage examples and sample outputs

## Project Structure

```
.claude/skills/clipper/
├── SKILL.md              # Main skill instructions (for Claude)
├── SEGMENT_TYPES.md      # Detailed segment criteria
├── EXAMPLES.md           # Usage examples
└── scripts/
    ├── parse_transcription.py   # Parse JSON transcription
    └── extract_clips.py         # Extract clips with precision & silence removal
```

## Requirements

- **Python 3.8+** (for scripts - no additional packages needed)
- **ffmpeg** (required for clip extraction - install with `brew install ffmpeg` on macOS or `apt-get install ffmpeg` on Linux)
- **jq** (optional, for filtering results)

## Sample Data

This repository includes sample data:
- `out.json`: Sample transcription (6+ hours, 4400 sentences)
- `Morning+Chillin.mp4`: Original video file
- `parsed.json`: Example parsed transcription output

## Try It Now

Just ask Claude in natural language:

```
"Find interesting clips from my video"
```

or

```
"Analyze my video transcription and find the top 10 most interesting clips"
```

Claude handles everything automatically! No manual script running needed.

## Why This Approach?

**Original plan**: Use Anthropic API to analyze transcriptions
- ❌ Requires API key setup
- ❌ Costs money per analysis
- ❌ Adds external dependency

**Current approach**: Claude Code analyzes directly
- ✅ Zero setup - just works
- ✅ No API costs
- ✅ Same model quality (Claude Sonnet 4.5)
- ✅ Better integration with your workflow
- ✅ Can customize on the fly with natural language

## Advanced Usage

### Filter by Category

```bash
# After Claude creates segments.json:
cat segments.json | jq '.clips[] | select(.category == "tip")'
```

### Sort by Duration

```bash
cat segments.json | jq '.clips | sort_by(.duration) | .[]'
```

### Get High-Confidence Clips Only

```bash
cat segments.json | jq '.clips[] | select(.confidence > 0.85)'
```

### Custom Analysis

Ask Claude to customize the analysis:
- "Find longer clips with more context, around 2-3 minutes"
- "Focus on teaching moments and tips"
- "Show me the most entertaining segments"
- "Find clips with strong opinions about AI"

## Troubleshooting

**No clips found**: Ask Claude to "lower the confidence threshold to 0.5"

**Too many clips**: Ask Claude to "only include clips with confidence above 0.8"

**Large files**: For very long videos (4+ hours), Claude will automatically analyze in windows

## Next Steps

1. Put your transcription JSON and video file in a directory
2. Ask Claude: "Find interesting clips from my video"
3. Claude handles parsing, analysis, and extraction automatically
4. Review your clips in the `clips/` directory
5. Share your clips!
