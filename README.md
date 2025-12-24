# Video Clipper Skill

A Claude Code skill for analyzing video transcriptions and automatically identifying the most interesting and clip-worthy segments.

## Quick Start

### 1. Parse Your Transcription

```bash
python .claude/skills/clipper/scripts/parse_transcription.py out.json > parsed.json
```

### 2. Ask Claude to Analyze

Simply ask Claude:
```
"Analyze parsed.json and find interesting clips for me"
```

Claude will analyze the transcription directly and create `segments.json` with all the interesting clips, timestamps, and metadata.

**No API setup needed!** Claude Code analyzes the transcription itself - no extra API keys or costs.

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

### Step 1: Parse Transcription
The `parse_transcription.py` script extracts sentences with timestamps from your JSON transcription file:

```bash
python .claude/skills/clipper/scripts/parse_transcription.py video.json > parsed.json
```

### Step 2: Claude Analyzes Directly
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

### Step 3: Extract Video Clips
Use the timestamps from `segments.json` to extract clips with ffmpeg.

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

Once you have `segments.json`, extract clips using ffmpeg:

```bash
# Extract a single clip
START_TIME=18.8
END_TIME=26.08
ffmpeg -i "Morning+Chillin.mp4" -ss $START_TIME -to $END_TIME -c copy clip_1.mp4

# Extract all clips automatically
mkdir -p clips
cat segments.json | jq -r '.clips[] | @json' | while read clip; do
  start=$(echo $clip | jq -r '.start_time')
  end=$(echo $clip | jq -r '.end_time')
  title=$(echo $clip | jq -r '.suggested_title' | tr ' ' '_')
  ffmpeg -i "Morning+Chillin.mp4" -ss $start -to $end -c copy "clips/${title}.mp4"
done
```

## Using with Claude Code

This is a Claude Code skill - it activates automatically when you work with video transcriptions.

**Example prompts:**
- "Analyze the transcription and find interesting clips"
- "What are the best moments to clip from this video?"
- "Find high-energy reactions in parsed.json"
- "Show me only tip segments with high confidence"
- "Find clips between 20-40 seconds long"

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
    └── parse_transcription.py   # Parse JSON transcription
```

## Requirements

- **Python 3.8+** (for parsing script only - no additional packages needed)
- **jq** (optional, for filtering results)
- **ffmpeg** (optional, for extracting video clips)

## Sample Data

This repository includes sample data:
- `out.json`: Sample transcription (6+ hours, 4400 sentences)
- `Morning+Chillin.mp4`: Original video file
- `parsed.json`: Example parsed transcription output

## Try It Now

```bash
# 1. Parse the sample transcription
python .claude/skills/clipper/scripts/parse_transcription.py out.json > parsed.json

# 2. Ask Claude
# "Analyze parsed.json and find the top 10 most interesting clips"

# 3. Review the results in segments.json

# 4. Extract clips with ffmpeg
```

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
- "Find only short clips under 30 seconds"
- "Focus on teaching moments and tips"
- "Show me the most entertaining segments"
- "Find clips with strong opinions about AI"

## Troubleshooting

**No clips found**: Ask Claude to "lower the confidence threshold to 0.5"

**Too many clips**: Ask Claude to "only include clips with confidence above 0.8"

**Large files**: For very long videos (4+ hours), Claude will automatically analyze in windows

## Next Steps

1. Parse your transcription: `python .claude/skills/clipper/scripts/parse_transcription.py your_video.json > parsed.json`
2. Ask Claude to analyze it
3. Review the identified clips in `segments.json`
4. Extract your favorite clips with ffmpeg
5. Share your clips!
