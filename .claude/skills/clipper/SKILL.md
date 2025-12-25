---
name: clipper
description: Analyze video transcriptions to identify interesting segments for clipping. Finds highlights, key moments, and reactions with precise timestamps. Use when working with video transcriptions to extract clip-worthy moments.
---

# Video Clipper Skill

Analyzes video transcription files to identify the most interesting and clip-worthy segments with precise timestamps.

## Quick Start

User just needs the transcription JSON and video file in their directory. When they ask you to analyze or find clips, you handle everything automatically:

```
User: "Find interesting clips from my video"
```

You will automatically:
1. Detect the transcription file (usually `out.json` or `*.json`)
2. Check if `parsed.json` exists, if not, run the parse script
3. Analyze `parsed.json` and create `segments.json`
4. Ask user if they want clips extracted
5. If yes, run extraction script automatically

## Execution Checklist

When user asks to find clips, follow this exact sequence:

**A. Detect Files**
- [ ] Check if `parsed.json` exists
- [ ] If not, look for transcription JSON (check `out.json` first, then `*.json`)
- [ ] Note: `segments.json` and other analysis files are NOT transcription files

**B. Parse (if needed)**
- [ ] If `parsed.json` doesn't exist, run: `python .claude/skills/clipper/scripts/parse_transcription.py <transcription> > parsed.json`
- [ ] Verify `parsed.json` was created successfully

**C. Analyze**
- [ ] Read `parsed.json` in windows (100-200 sentences at a time)
- [ ] Identify clip-worthy segments using the 7 categories below
- [ ] Write results to `segments.json`
- [ ] Report summary to user (number of clips found, categories, etc.)

**D. Extract (optional)**
- [ ] Ask user if they want to extract clips now
- [ ] If yes, detect video file (`*.mp4`, `*.mov`, `*.mkv`)
- [ ] Run: `python .claude/skills/clipper/scripts/extract_clips.py segments.json <transcription> <video> clips/`
- [ ] Monitor output and report results

**E. Cleanup (optional post-processing)**
- [ ] Ask user if they want to clean up clips (remove fillers and silences)
- [ ] If yes, run: `python .claude/skills/clipper/scripts/cleanup_clips.py segments.json <transcription> <video> clips/`
- [ ] Cleaned clips are saved to `clips/cleaned/`
- [ ] Report cleanup stats (fillers removed, silences removed, time saved)

## Workflow

### Step 1: Parse Transcription (Automatic)

When a user asks you to find clips, FIRST check if `parsed.json` exists. If not, automatically run:

```bash
python .claude/skills/clipper/scripts/parse_transcription.py <transcription_file> > parsed.json
```

**How to detect the transcription file:**
- Look for `out.json` in current directory
- If not found, look for any `*.json` file that contains a `sentences` array
- Ask user if multiple JSON files are found

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
  "total_clips": 148,
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
      "topic": "tiktok_streaming",
      "subtopic": "vertical_discovery",
      "keywords": ["tiktok", "streaming", "vertical", "discovery"],
      "confidence": 0.92,
      "suggested_title": "TikTok Vertical Streaming Discovery",
      "key_quote": "Oh my god, that's incredible.",
      "first_sentence": "Oh my god, that's incredible.",
      "last_sentence": "Didn't know I could stream like that.",
      "total_sentences": 3,
      "context_expansion": {
        "sentences_added_before": 0,
        "sentences_added_after": 0,
        "reason": "Segment was self-contained from initial identification"
      },
      "coherence_validated": true
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

- **Duration**: Between 30-180 seconds (ideal: 60-120 seconds for context-rich clips)
- **Completeness**: Must be complete thoughts, not cut mid-sentence
- **Self-contained**: Understandable without prior video context (include setup/context before key moments)
- **Natural boundaries**: Start/end at logical points in speech
- **Confidence threshold**: Only include segments with confidence ≥ 0.6
- **Context**: Consider including 10-30 seconds of setup/context before the key moment

#### CRITICAL: Sentence Integrity Rules

EVERY segment MUST:
1. ✓ **Start at the BEGINNING of a sentence** (first word of sentence at start_index)
2. ✓ **End at the END of a sentence** (last word of sentence at end_index)
3. ✗ **NEVER include partial sentences**
4. ✗ **NEVER start mid-sentence**
5. ✗ **NEVER end mid-sentence**

**Validation:**
- First sentence should start naturally (capital letter, proper start)
- Last sentence should end completely (period, question mark, or exclamation mark)
- All sentences between start_index and end_index must be complete
- No dangling references ("it", "this", "that") without clear antecedent in the segment

#### Context Expansion Algorithm

After identifying an interesting moment at sentence N, expand for coherence:

**Step 1: Check if first sentence needs context**

Does the first sentence:
- Reference "this", "that", "it" without clear antecedent?
- Use "so", "therefore", "because" implying prior setup?
- Start with "And", "But", "Or" (continuation word)?
- Assume knowledge from earlier in video?

→ **If YES**: Include sentence N-1, then re-check
→ **Maximum lookback**: 3 sentences

**Step 2: Check if last sentence feels complete**

Does the last sentence:
- End with ellipsis or trailing thought?
- Start explanation but not finish? (e.g., "The way this works is...")
- Ask a question without providing an answer?
- Feel like it's cut off mid-thought?

→ **If YES**: Include sentence N+1, then re-check
→ **Maximum lookahead**: 2 sentences

**Step 3: Verify duration**
- After context expansion, check total duration still within 30-180 seconds
- If too long after expansion, find natural sub-division point

#### Coherence Validation Checklist

For EACH segment, verify all of these before including:

- [ ] **Sentence Boundaries**: Starts at beginning and ends at end of complete sentences
- [ ] **No Unclear Pronouns**: First sentence doesn't use "it", "this", "that" referring to unknown context
- [ ] **Self-Contained**: Can be understood without watching prior video
- [ ] **Complete Thought**: Has beginning (setup), middle (content), and end (resolution)
- [ ] **Natural Start**: Doesn't start with continuation words without context
- [ ] **Natural End**: Doesn't end mid-explanation, feels like natural stopping point
- [ ] **Duration Check**: After expansion, still within 30-180 second range

If any check fails, expand context or skip the segment.

#### Topic and Keyword Extraction

For each identified segment, extract hierarchical topics and keywords:

**1. Extract Keywords (Automatic, No Hard-Coding)**
- Identify capitalized proper nouns: "TikTok", "Redis", "OAuth", "MediaPipe"
- Extract technical terms: "authentication", "database", "API", "deployment"
- Find recurring noun phrases: "user login", "token validation", "cache setup"
- Rank by prominence and select top 3-5 keywords

**2. Determine Topic (Broad Category)**
- Use most prominent keyword as topic
- Convert to lowercase with underscores: "tiktok_api", "authentication", "redis_setup"
- Topic represents the general subject area of the segment

**3. Determine Subtopic (Specific Aspect)**
- Identify specific action or aspect within the topic
- Look for action words: "setup", "config", "debug", "deploy", "test", "install"
- Combine with context: "oauth_setup", "token_validation", "cache_configuration"
- Subtopic represents what you're doing with the topic

**4. Example Topic Hierarchy**
```
Segment text: "So I'm setting up OAuth for the authentication system using Google's API..."
Keywords: ["oauth", "authentication", "google", "api", "setup"]
Topic: "authentication"
Subtopic: "oauth_setup"
```

```
Segment text: "The Redis cache is throwing errors when I try to deploy to production..."
Keywords: ["redis", "cache", "errors", "deploy", "production"]
Topic: "redis"
Subtopic: "deployment_debugging"
```

#### Multi-step Process

Since the parsed transcription may be large, analyze it in steps with overlapping windows:

1. **Get total count**: Read the parsed.json metadata to see total sentences

2. **Analyze in overlapping windows**: Use 200-sentence windows with 50-sentence overlap
   - Window 1: Sentences 0-200
   - Window 2: Sentences 150-350 (50 overlap)
   - Window 3: Sentences 300-500 (50 overlap)
   - Continue until all sentences analyzed
   - **Why overlap?** Prevents splitting trains of thought mid-context

3. **Track all segments**: Keep a running list of all identified clips with topic/subtopic/keywords

4. **Deduplicate segments**: If same segment appears in multiple windows
   - Check for overlapping sentence ranges (e.g., 160-175 found in both Window 1 and 2)
   - Keep only one instance (highest confidence version)
   - Merge if boundaries slightly differ but clearly same segment

5. **Group by topic**: Organize segments by their topic field
   - Group all segments with topic="authentication"
   - Group all segments with topic="redis"
   - etc.

6. **Create compilations automatically**: For each topic with 2+ segments
   - Create compilation entry with:
     - Unique ID (comp_auth, comp_redis, etc.)
     - Title based on topic and subtopics
     - List of segment indices (references to clips array)
     - Total talking duration (sum of segment durations)
     - Time span (from first to last segment)
   - **Gap handling**: Gaps between segments are automatically removed during extraction
   - If a gap contains another segment with the same topic, that segment is included

7. **Sort clips**: Final clips array sorted by confidence score (highest first)

8. **Write output**: Create segments.json with:
   - All individual clips with topic/subtopic/keywords
   - All compilations
   - Updated metadata including compilation count

#### Step-by-Step Segment Identification with Validation

When analyzing transcription, follow this process for EACH potential clip:

**1. Identify Interesting Moment**
- Scan sentences for patterns matching the 7 categories
- Note the key sentence(s) containing the interesting moment
- Example: Sentence 436 has high-energy reaction

**2. Determine Initial Sentence Boundaries**
- Identify complete sentence containing the moment
- Example: Sentences 436-438 contain the core content

**3. Run Context Expansion Algorithm**
- Check first sentence for context needs (pronouns, continuation words)
- If needed, expand backward (max 3 sentences)
- Check last sentence for completeness
- If needed, expand forward (max 2 sentences)
- Example: Added sentences 434-435 for context

**4. Validate Coherence Checklist**
- Verify all items in coherence checklist
- Ensure sentence boundaries are intact
- Confirm self-containment
- Check that first/last sentences make sense

**5. Extract Metadata**
- Record first_sentence and last_sentence text
- Count total_sentences
- Document context_expansion (how many added and why)
- Set coherence_validated: true

**6. Create Segment Entry**
- Include all required fields
- Add validation metadata
- Ensure timestamps correspond to complete sentences

**7. Final Validation**
- Re-read segment text as if you've never seen the video
- Ask: "Would this make complete sense standalone?"
- If NO: expand further or skip segment
- If YES: add to clips array

#### Example Analysis Command Flow

```bash
# User asks Claude:
"Find interesting clips from my video"

# Claude automatically:
# 1. Checks if parsed.json exists, creates it if needed
# 2. Reads parsed.json to understand structure (4400 sentences, 6.7 hours)
# 3. Analyzes in overlapping windows:
#    - Window 1: Sentences 0-200
#    - Window 2: Sentences 150-350
#    - Window 3: Sentences 300-500
#    - ... (continues to end)
# 4. For each segment: extracts keywords, determines topic/subtopic
# 5. Deduplicates segments found in multiple windows
# 6. Groups segments by topic
# 7. Auto-creates compilations for topics with 2+ segments
# 8. Writes segments.json with clips + compilations
# 9. Reports summary:
#    "Found 148 clips across 12 topics. Created 12 compilations."
```

#### Example Analysis Output

```
Analysis complete! Found 148 individual clips.

Topics detected:
  • authentication (5 segments, 312s total) → Compilation created
  • redis_setup (3 segments, 198s total) → Compilation created
  • tiktok_api (4 segments, 256s total) → Compilation created
  • mediapipe (6 segments, 445s total) → Compilation created
  • frontend_debugging (2 segments, 128s total) → Compilation created
  ... (7 more topics)

Created 12 compilations automatically.

Output saved to segments.json
  - 148 individual clips
  - 12 topic compilations

Want to extract clips now?
```

### Step 3: Review Identified Segments

After analysis, review `segments.json`:
- **Individual clips**: All identified segments sorted by confidence (highest first)
- **Topic metadata**: Each clip includes topic, subtopic, and keywords
- **Compilations**: Automatically created for topics with 2+ segments
- Each segment includes:
  - Precise timestamps for video extraction
  - Category and reason explaining why it's interesting
  - Hierarchical topic information
  - Suggested title for the clip

### Step 4: Extract Video Clips (Automatic)

After creating `segments.json`, ask the user if they want to extract the clips. If yes, automatically detect the video file and run:

```bash
python .claude/skills/clipper/scripts/extract_clips.py segments.json <original_transcription> <video_file> clips/
```

**How to detect files:**
- Original transcription: Use the same file from Step 1 (usually `out.json`)
- Video file: Look for `*.mp4`, `*.mov`, or `*.mkv` in current directory
- Ask user if multiple video files are found

**Features:**
- **Word-level precision**: Uses word timestamps for exact boundaries
- **Safety buffer**: Adds 0.1s before/after to avoid clipping inside words
- **Coherent extraction**: Extracts exactly what analysis identified (no splitting)
- **Compilation support**: Automatically creates topic-based compilations from multiple segments
- **Length constraints**: Individual clips 1-6 min, compilations can be longer
- **FFmpeg integration**: Generates high-quality MP4 clips

**Arguments:**
1. `segments.json` - Output from Step 2 analysis
2. `out.json` - Original transcription with word-level data
3. `video.mp4` - Source video file
4. `clips/` - Output directory (optional, defaults to "clips/")

**How it works for individual clips:**
1. Loads word-level timestamps from original transcription
2. For each segment, finds first and last words from sentence boundaries
3. Applies 0.1s safety buffer before first word and after last word
4. Checks if total duration is within 60s-360s range
5. Extracts one continuous clip using ffmpeg
6. Preserves natural speech flow with no splitting

**How it works for compilations:**
1. Reads compilation definition from segments.json
2. Retrieves all referenced segments by index
3. Sorts segments chronologically (by start_index)
4. For each segment in the compilation:
   - Extracts as coherent temporary clip
5. Combines all segments into one long compilation clip
6. Gaps between segments are automatically removed
7. Saves with "comp_" prefix: `comp_auth_Complete_Authentication.mp4`

**Configuration** (edit extract_clips.py to adjust):
- `SAFETY_BUFFER = 0.1` - Buffer before/after words (seconds)
- `MIN_CLIP_LENGTH = 60.0` - Minimum total clip length (1 minute)
- `MAX_CLIP_LENGTH = 360.0` - Maximum total clip length (6 minutes)

**Output:**
- Individual clips: `001_Clip_Title.mp4`, `002_Another_Clip.mp4`, etc.
- Compilations: `comp_auth_Complete_Authentication.mp4`, `comp_redis_Redis_Setup.mp4`, etc.
- Individual clips too short (<1min) or too long (>6min) are skipped
- Compilations can exceed 6 minutes (contain multiple segments)
- Summary stats printed: individual clips extracted, compilations created, skipped

### Step 5: Cleanup Clips (Optional Post-Processing)

After extracting coherent clips, optionally clean them up by removing filler words and silences:

```bash
python .claude/skills/clipper/scripts/cleanup_clips.py segments.json <original_transcription> <video_file> clips/
```

**This is a SEPARATE post-processing phase:**
- Phase 1 (Analysis): Identify coherent segments with complete sentences ✓
- Phase 2 (Extraction): Extract exactly what analysis identified ✓
- Phase 3 (Cleanup): Remove fillers and silences ← THIS STEP

**Features:**
- **Filler word removal**: Removes "um", "uh", "ah", "like", etc.
- **Silence removal**: Detects and removes gaps > 0.4s between words
- **Segment combining**: Merges remaining parts into polished clips
- **Preserves coherence**: Only removes fillers/silences, maintains sentence structure

**How it works:**
1. For each extracted clip, loads word-level timestamps
2. Identifies and removes filler words
3. Detects silence gaps > 0.4s between remaining words
4. Re-extracts from original video, skipping fillers and silences
5. Combines remaining segments into cleaned clip
6. Saves to `clips/cleaned/` directory

**Configuration** (edit cleanup_clips.py to adjust):
- `SAFETY_BUFFER = 0.1` - Buffer before/after cuts (seconds)
- `SILENCE_THRESHOLD = 0.4` - Min gap to consider silence (seconds)
- `MIN_SEGMENT_LENGTH = 0.3` - Min segment length to keep (seconds)
- `FILLER_WORDS` - Set of filler words to remove

**Output:**
- Original clips preserved in `clips/`
- Cleaned clips saved to `clips/cleaned/`
- Summary stats: fillers removed, silences removed, time saved

## What Makes a Good Clip?

See the criteria in Step 2 above, or review [SEGMENT_TYPES.md](SEGMENT_TYPES.md) for detailed guidance on each category.

## Configuration

You can adjust these parameters when analyzing:

- **MIN_CLIP_LENGTH**: 30 seconds (ideal range for analysis, extraction enforces 60s minimum)
- **MAX_CLIP_LENGTH**: 180 seconds (ideal range for analysis, extraction allows up to 360s)
- **CONFIDENCE_THRESHOLD**: 0.6 (only include clips above this score)
- **WINDOW_SIZE**: 100 sentences per analysis window

Note: The extraction script enforces 60s minimum and 360s maximum to ensure clips have sufficient context.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for sample analyses and outputs.

## Requirements

- **Python 3.8+** for the scripts (no additional packages needed)
- **ffmpeg** for video clip extraction (install: `brew install ffmpeg` on macOS or `apt-get install ffmpeg` on Linux)

## Troubleshooting

**"No segments found"**: The content may be low-energy or monotone. Try lowering confidence threshold mentally to 0.5 or including shorter clips (down to 8 seconds).

**"Too many segments"**: Raise confidence threshold to 0.75+ or increase minimum length to 15-20 seconds.

**Large files**: For very long videos (4+ hours), analyze in smaller windows and take breaks to avoid context limits.
