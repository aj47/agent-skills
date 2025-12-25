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
3. ✅ Extract topics and keywords from your content
4. ✅ Create automatic compilations for related segments
5. ✅ Create `segments.json` with all clips and compilations
6. ✅ Ask if you want to extract the clips
7. ✅ Extract all clips and compilations with word-level precision

**No API setup needed!** Claude Code handles everything - no extra API keys or costs.

Automatically extracts all clips with:
- **Coherent sentences** - Complete thoughts with proper sentence boundaries
- **Word-level precision** - Uses exact word timestamps with 0.1s safety buffer
- **Hierarchical topic extraction** - Automatically identifies topics and subtopics from content
- **Automatic compilations** - Combines related segments on the same topic into longer clips
- **Context validation** - Ensures clips are self-contained and understandable standalone
- **Length constraints** - Individual clips 1-6 min, compilations can be longer
- **High quality** - Re-encodes with H.264 for perfect timing
- **No post-processing** - Extracts exactly what analysis identifies, preserving natural speech

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
- Hierarchical topic information (topic, subtopic, keywords)
- Confidence score (0.0-1.0)
- Suggested clip title
- Key quote

## Topics & Compilations

The skill automatically organizes clips by topic and creates compilations:

**Hierarchical Topics:**
- **Topic**: Broad category (e.g., "authentication", "redis_setup", "tiktok_api")
- **Subtopic**: Specific aspect (e.g., "oauth_setup", "deployment_debugging")
- **Keywords**: 3-5 key terms extracted from the segment

**Automatic Compilations:**
- When 2+ segments share the same topic, a compilation is automatically created
- Compilations combine all related segments into one long-form clip
- Gaps between segments are removed (smart gap handling)
- Perfect for creating comprehensive tutorials from scattered discussions

**Example:**
```
You discuss authentication at:
  - 0:10-0:15 (OAuth setup)
  - 0:45-0:52 (Token configuration)
  - 1:30-1:40 (Testing)

Result:
  • 3 individual clips (if each meets length requirements)
  • 1 compilation: "Complete Authentication Implementation" (~8 minutes, no gaps)
```

## How It Works

### Fully Automatic Workflow

When you ask Claude to find clips from your video, it automatically:

**Step 1: Parse Transcription** (if needed)
- Detects your transcription file (usually `out.json`)
- Runs `parse_transcription.py` to create a simplified version
- Caches result as `parsed.json` for faster future analysis

**Step 2: Analyze for Clip-Worthy Moments**
Claude reads the parsed transcription and:
1. Analyzes sentences in overlapping windows (50-sentence overlap to preserve context)
2. Identifies clip-worthy moments based on 7 categories
3. Extracts topics, subtopics, and keywords from each segment
4. Groups segments by topic
5. Auto-creates compilations for topics with 2+ segments
6. Assigns confidence scores
7. Creates `segments.json` with all clips and compilations

**Why this approach?**
- ✅ No API costs - uses Claude Code itself
- ✅ No API key setup required
- ✅ Better integration with your workflow
- ✅ Same high-quality analysis from Claude Sonnet 4.5

**Step 3: Extract Video Clips** (optional)
Claude asks if you want clips extracted, then automatically:
- Detects your video file (looks for `*.mp4`, `*.mov`, etc.)
- Runs `extract_clips.py` with the right parameters
- Extracts all individual clips to `clips/` directory
- Extracts all compilations (multi-segment clips combined together)
- Outputs both individual clips (001_Title.mp4) and compilations (comp_auth_Title.mp4)

**Features:**
- Uses word-level timestamps for frame-perfect accuracy
- Adds 0.1s buffer before/after to avoid clipping mid-word
- Extracts complete, coherent sentences as identified during analysis
- No post-processing or splitting - preserves natural speech flow
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
  "total_clips": 148,
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
      "topic": "tiktok_streaming",
      "subtopic": "vertical_discovery",
      "keywords": ["tiktok", "streaming", "vertical", "discovery"],
      "confidence": 0.92,
      "suggested_title": "TikTok Vertical Streaming Discovery",
      "key_quote": "Oh my god, that's incredible."
    }
  ],
  "compilations": [
    {
      "id": "comp_auth",
      "title": "Complete Authentication Implementation",
      "topic": "authentication",
      "subtopics": ["oauth_setup", "token_config", "testing"],
      "segment_indices": [5, 12, 34, 67, 89],
      "total_segments": 5,
      "talking_duration": 312.5,
      "time_span": 3600.0,
      "created_automatically": true
    }
  ],
  "metadata": {
    "total_sentences_analyzed": 4400,
    "total_duration": 24165.0,
    "min_clip_length": 30,
    "max_clip_length": 180,
    "confidence_threshold": 0.6,
    "individual_clips": 148,
    "compilations_created": 12
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

The `extract_clips.py` script automatically extracts all clips:

```bash
python .claude/skills/clipper/scripts/extract_clips.py segments.json out.json "Morning+Chillin.mp4" clips/
```

### Word-Level Precision

The script uses word-level timestamps for frame-perfect extraction:
1. Loads word-level timestamps from the original transcription
2. Finds the exact first and last words of each coherent segment
3. Adds a 0.1s safety buffer before/after to prevent clipping mid-word
4. Results in frame-perfect clip boundaries

### Coherent Extraction

The script extracts clips exactly as identified during analysis:
- **No post-processing**: Preserves natural speech flow
- **Complete sentences**: Always starts and ends at sentence boundaries
- **Context preservation**: Includes all context needed for standalone understanding
- **One continuous clip**: Each segment extracted as a single video file

**Example:** A 2-minute coherent segment about authentication:
1. Analysis identifies complete thought from sentence 45 to sentence 52
2. Extraction uses word timestamps: first word of sentence 45 to last word of sentence 52
3. Adds 0.1s buffer on each end
4. Result: `005_Authentication_Setup.mp4` (single continuous clip with complete thought)

### Configuration

Edit `scripts/extract_clips.py` to adjust:

```python
SAFETY_BUFFER = 0.1     # Buffer before/after words (seconds)
MIN_CLIP_LENGTH = 60.0  # Minimum total clip length (1 minute)
MAX_CLIP_LENGTH = 360.0 # Maximum total clip length (6 minutes)
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
"Analyze my video transcription and find interesting clips"
```

Claude automatically:
- Finds all clip-worthy moments
- Extracts topics and keywords
- Creates compilations for related segments
- Handles everything with zero manual intervention!

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
