# Examples

This document shows example workflows and outputs from the video clipper skill.

## Example 1: Tech Tutorial Video

### Input Transcription Excerpt

```
[0] (2.56s - 3.68s): TikTok.
[1] (3.68s - 5.20s): Is this gonna work?
[2] (5.44s - 18.80s): Yo, it says we are streaming. No, I don't.
[3] (18.80s - 23.04s): Oh my god, that's incredible.
[4] (23.44s - 26.08s): Didn't know I could stream like that.
[5] (26.48s - 30.72s): I don't really know how it works, but it seems like you can go live vertically without having to go live on YouTube.
[6] (30.72s - 32.56s): Which is new to me. I didn't know that was the case.
```

### Output Segments

```json
{
  "total_clips": 2,
  "clips": [
    {
      "start_time": 18.80,
      "end_time": 26.08,
      "duration": 7.28,
      "text": "Oh my god, that's incredible. Didn't know I could stream like that.",
      "reason": "High-energy reaction to discovering new streaming capability - genuine surprise moment that's highly relatable",
      "category": "reaction",
      "confidence": 0.92,
      "suggested_title": "TikTok Vertical Streaming Discovery",
      "key_quote": "Oh my god, that's incredible."
    },
    {
      "start_time": 26.48,
      "end_time": 32.56,
      "duration": 6.08,
      "text": "I don't really know how it works, but it seems like you can go live vertically without having to go live on YouTube. Which is new to me. I didn't know that was the case.",
      "reason": "Informative tip about TikTok vertical streaming - valuable insight for content creators",
      "category": "tip",
      "confidence": 0.78,
      "suggested_title": "TikTok Vertical Streaming Tip",
      "key_quote": "you can go live vertically without having to go live on YouTube"
    }
  ],
  "metadata": {
    "total_sentences": 7,
    "total_duration": 32.56,
    "window_size": 50,
    "min_clip_length": 10,
    "max_clip_length": 60,
    "confidence_threshold": 0.6
  }
}
```

---

## Example 2: Q&A Session

### Input Transcription Excerpt

```
[45] (180.00s - 185.20s): Let me know what questions you have.
[46] (185.20s - 189.50s): Someone asked about local LLMs.
[47] (189.50s - 195.30s): So if you have a Mac, I recommend getting MLX models.
[48] (195.30s - 200.15s): That's one tip I guess if you didn't know about that.
[49] (200.15s - 207.80s): Otherwise like I recommend LM Studio. I really think LM Studio is great for running local LLMs.
[50] (207.80s - 215.40s): But honestly, I don't really run local LLMs anymore because it's just really not worth it for me.
[51] (215.40s - 222.10s): The intelligence I can get and the speed I can get from the API models is way better.
[52] (222.10s - 228.90s): And yeah, I'm never gonna match that unless I spend like a hundred thousand dollars.
```

### Output Segments

```json
{
  "total_clips": 2,
  "clips": [
    {
      "start_time": 189.50,
      "end_time": 200.15,
      "duration": 10.65,
      "text": "So if you have a Mac, I recommend getting MLX models. That's one tip I guess if you didn't know about that.",
      "reason": "Concrete technical recommendation with specific tool mention - actionable advice for Mac users",
      "category": "tip",
      "confidence": 0.88,
      "suggested_title": "Best Local LLM for Mac Users",
      "key_quote": "I recommend getting MLX models"
    },
    {
      "start_time": 207.80,
      "end_time": 228.90,
      "duration": 21.10,
      "text": "But honestly, I don't really run local LLMs anymore because it's just really not worth it for me. The intelligence I can get and the speed I can get from the API models is way better. And yeah, I'm never gonna match that unless I spend like a hundred thousand dollars.",
      "reason": "Controversial hot take on local vs cloud LLMs with specific cost reasoning - debate-worthy opinion",
      "category": "opinion",
      "confidence": 0.85,
      "suggested_title": "Why I Stopped Using Local LLMs",
      "key_quote": "I don't really run local LLMs anymore"
    }
  ]
}
```

---

## Example 3: Story-Based Content

### Input Transcription Excerpt

```
[100] (420.00s - 425.50s): So this one time, I was trying to debug this issue for hours.
[101] (425.50s - 432.20s): Like literally five hours straight, just staring at the code.
[102] (432.20s - 438.80s): And then I realized I had a typo in the environment variable name.
[103] (438.80s - 443.40s): It was supposed to be underscore but I wrote a dash.
[104] (443.40s - 449.10s): Five hours! For a single character!
[105] (449.10s - 455.70s): That's when I learned to always use a linter for your config files.
```

### Output Segments

```json
{
  "total_clips": 1,
  "clips": [
    {
      "start_time": 420.00,
      "end_time": 455.70,
      "duration": 35.70,
      "text": "So this one time, I was trying to debug this issue for hours. Like literally five hours straight, just staring at the code. And then I realized I had a typo in the environment variable name. It was supposed to be underscore but I wrote a dash. Five hours! For a single character! That's when I learned to always use a linter for your config files.",
      "reason": "Relatable debugging story with dramatic build-up, punchline, and lesson learned - entertaining and educational",
      "category": "story",
      "confidence": 0.91,
      "suggested_title": "5 Hours Lost to One Character",
      "key_quote": "Five hours! For a single character!"
    }
  ]
}
```

---

## Usage Examples

### Basic Workflow

```bash
# 1. Parse transcription
python .claude/skills/clipper/scripts/parse_transcription.py video_transcript.json > parsed.json

# 2. Analyze for clips
python .claude/skills/clipper/scripts/analyze_segments.py parsed.json > segments.json

# 3. View results
cat segments.json | jq '.clips[] | {title: .suggested_title, time: "\(.start_time)-\(.end_time)", category, confidence}'
```

**Output:**
```json
{
  "title": "TikTok Vertical Streaming Discovery",
  "time": "18.8-26.08",
  "category": "reaction",
  "confidence": 0.92
}
{
  "title": "Best Local LLM for Mac Users",
  "time": "189.5-200.15",
  "category": "tip",
  "confidence": 0.88
}
```

---

### Filtering by Category

```bash
# Get only high-confidence tips
cat segments.json | jq '.clips[] | select(.category == "tip" and .confidence > 0.8)'
```

---

### Filtering by Confidence

```bash
# Get only clips with confidence > 0.85
cat segments.json | jq '.clips[] | select(.confidence > 0.85)'
```

---

### Sorting by Duration

```bash
# Get clips sorted by duration
cat segments.json | jq '.clips | sort_by(.duration) | .[]'
```

---

## Integration with Video Editing

### Using ffmpeg to Extract Clips

Once you have the segments, you can extract them from the original video:

```bash
# Extract a single clip
START_TIME=18.8
END_TIME=26.08
ffmpeg -i original_video.mp4 -ss $START_TIME -to $END_TIME -c copy clip_1.mp4

# Extract all clips automatically
cat segments.json | jq -r '.clips[] | @json' | while read clip; do
  start=$(echo $clip | jq -r '.start_time')
  end=$(echo $clip | jq -r '.end_time')
  title=$(echo $clip | jq -r '.suggested_title' | tr ' ' '_')
  ffmpeg -i original_video.mp4 -ss $start -to $end -c copy "clips/${title}.mp4"
done
```

---

## Expected Output Format

Every analysis will return this structure:

```json
{
  "total_clips": 5,
  "clips": [
    {
      "start_time": 123.45,       // Start timestamp in seconds
      "end_time": 145.67,         // End timestamp in seconds
      "duration": 22.22,          // Duration in seconds
      "text": "Full text...",     // Complete transcript text
      "reason": "Why this...",    // Explanation for selection
      "category": "reaction",     // Category type
      "confidence": 0.85,         // Confidence score (0.0-1.0)
      "suggested_title": "...",   // Suggested clip title
      "key_quote": "..."          // Most important quote
    }
  ],
  "metadata": {
    "total_sentences": 1000,
    "total_duration": 3600.0,
    "window_size": 50,
    "min_clip_length": 10,
    "max_clip_length": 60,
    "confidence_threshold": 0.6
  }
}
```

---

## Customization Examples

### Adjusting Parameters

Edit `scripts/analyze_segments.py` to customize:

```python
# Longer clips for in-depth content
MIN_CLIP_LENGTH = 20
MAX_CLIP_LENGTH = 90

# Higher quality threshold
CONFIDENCE_THRESHOLD = 0.75

# Smaller windows for shorter videos
WINDOW_SIZE = 30
```

### Category-Specific Analysis

Modify the prompt in `analyze_segments.py` to focus on specific categories:

```python
# Focus only on teaching content
ANALYSIS_PROMPT = """
Focus specifically on teaching moments and educational content.
Look for:
- Technical explanations
- How-to instructions
- Problem-solving demonstrations
- Concept breakdowns

Ignore reactions, humor, and opinions unless they include educational value.
"""
```

---

## Troubleshooting Examples

### No Clips Found

```json
{
  "total_clips": 0,
  "clips": [],
  "metadata": {...}
}
```

**Possible reasons:**
- Content is too monotone or low-energy
- Segments are too short (below MIN_CLIP_LENGTH)
- Confidence threshold is too high
- Video is mostly filler or transition content

**Solutions:**
- Lower CONFIDENCE_THRESHOLD to 0.5
- Reduce MIN_CLIP_LENGTH to 8 seconds
- Check if the transcription is accurate

### Too Many Clips

If you get 50+ clips from a 30-minute video:

**Solutions:**
- Raise CONFIDENCE_THRESHOLD to 0.75 or 0.8
- Increase MIN_CLIP_LENGTH to 15 or 20 seconds
- Review the top 10-15 clips by confidence score

### Overlapping Clips

The script automatically merges overlapping clips, but if you notice issues:

```python
# Increase the merge threshold in analyze_segments.py
# Change from 5 to 10 seconds
if next_clip['start_time'] <= current['end_time'] + 10:
```
