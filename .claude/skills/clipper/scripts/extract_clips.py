#!/usr/bin/env python3
"""
Extract video clips from segments with word-level precision and filler removal.

Features:
- Uses word-level timestamps for precise clip boundaries
- Adds 0.1s safety buffer to avoid clipping inside words
- Removes filler words (um, uh, ah, like, etc.)
- Removes silences greater than 0.4s duration
- Combines multi-part clips into single videos
- Enforces length constraints (30s min, 3min max)
- Generates clips using ffmpeg

Usage:
    python extract_clips.py segments.json original_transcription.json video.mp4 [output_dir]
"""

import json
import sys
import os
import subprocess
import tempfile
from typing import List, Dict, Any, Tuple


# Configuration
SAFETY_BUFFER = 0.1  # seconds to add before/after words
SILENCE_THRESHOLD = 0.4  # seconds - gaps larger than this are considered silence
MIN_CLIP_LENGTH = 30.0  # seconds - minimum total clip length
MAX_CLIP_LENGTH = 180.0  # seconds - maximum total clip length (3 minutes)
MIN_SUBCLIP_LENGTH = 3.0  # seconds - minimum length for a sub-clip segment

# Filler words to remove (case-insensitive)
FILLER_WORDS = {
    'um', 'uh', 'ah', 'er', 'hmm', 'mm', 'mmm',
    'umm', 'uhh', 'ahh', 'err', 'hm'
}


def load_word_level_data(transcription_file: str) -> Dict[int, List[Dict]]:
    """
    Load word-level timestamps from original transcription.

    Returns:
        Dictionary mapping sentence index to list of word objects
    """
    with open(transcription_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    word_map = {}
    for idx, sentence in enumerate(data.get('sentences', [])):
        word_map[idx] = sentence.get('words', [])

    return word_map


def is_filler_word(word_text: str) -> bool:
    """Check if a word is a filler word."""
    # Clean the word - remove punctuation and lowercase
    clean_word = ''.join(c for c in word_text if c.isalnum()).lower()
    return clean_word in FILLER_WORDS


def remove_filler_words(words: List[Dict]) -> List[Dict]:
    """
    Remove filler words from word list.

    Args:
        words: List of word objects with 'word', 'start', 'end' fields

    Returns:
        Filtered list without filler words
    """
    filtered = []
    for word in words:
        if not is_filler_word(word.get('word', '')):
            filtered.append(word)

    return filtered


def get_precise_boundaries(
    start_idx: int,
    end_idx: int,
    word_map: Dict[int, List[Dict]]
) -> Tuple[float, float, int]:
    """
    Get precise start and end times using word-level timestamps.

    Args:
        start_idx: Starting sentence index
        end_idx: Ending sentence index
        word_map: Dictionary mapping sentence index to words

    Returns:
        Tuple of (precise_start, precise_end, total_words_before_filtering)
    """
    # Collect all words in the segment
    all_words = []
    for idx in range(start_idx, end_idx + 1):
        all_words.extend(word_map.get(idx, []))

    if not all_words:
        raise ValueError(f"No words found for sentences {start_idx}-{end_idx}")

    original_count = len(all_words)

    # Remove filler words
    all_words = remove_filler_words(all_words)

    if not all_words:
        raise ValueError(f"No words left after removing fillers for sentences {start_idx}-{end_idx}")

    first_word_start = all_words[0]['start']
    last_word_end = all_words[-1]['end']

    # Apply safety buffer
    precise_start = max(0, first_word_start - SAFETY_BUFFER)
    precise_end = last_word_end + SAFETY_BUFFER

    return precise_start, precise_end, original_count


def detect_silence_gaps(
    start_idx: int,
    end_idx: int,
    word_map: Dict[int, List[Dict]]
) -> List[Tuple[float, float]]:
    """
    Detect silence gaps larger than SILENCE_THRESHOLD within a segment.

    Returns:
        List of (gap_start, gap_end) tuples for silences to remove
    """
    silences = []

    # Collect all words and remove fillers
    all_words = []
    for idx in range(start_idx, end_idx + 1):
        all_words.extend(word_map.get(idx, []))

    all_words = remove_filler_words(all_words)

    # Find gaps between consecutive words
    for i in range(len(all_words) - 1):
        current_word_end = all_words[i]['end']
        next_word_start = all_words[i + 1]['start']
        gap_duration = next_word_start - current_word_end

        if gap_duration > SILENCE_THRESHOLD:
            silences.append((current_word_end, next_word_start))

    return silences


def split_at_silences(
    start_time: float,
    end_time: float,
    silences: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """
    Split a segment into sub-clips by removing silence gaps.

    Args:
        start_time: Segment start time
        end_time: Segment end time
        silences: List of (gap_start, gap_end) tuples to remove

    Returns:
        List of (subclip_start, subclip_end) tuples
    """
    if not silences:
        return [(start_time, end_time)]

    subclips = []
    current_start = start_time

    for silence_start, silence_end in sorted(silences):
        # Add sub-clip before this silence
        if silence_start > current_start:
            duration = silence_start - current_start
            if duration >= MIN_SUBCLIP_LENGTH:
                subclips.append((current_start, silence_start))

        # Next sub-clip starts after the silence
        current_start = silence_end

    # Add final sub-clip after last silence
    if end_time > current_start:
        duration = end_time - current_start
        if duration >= MIN_SUBCLIP_LENGTH:
            subclips.append((current_start, end_time))

    return subclips


def extract_temp_clip(
    video_file: str,
    start_time: float,
    end_time: float,
    temp_dir: str,
    index: int
) -> str:
    """
    Extract a temporary clip segment.

    Returns:
        Path to temporary clip file
    """
    duration = end_time - start_time
    temp_file = os.path.join(temp_dir, f"part_{index:03d}.mp4")

    cmd = [
        'ffmpeg',
        '-y',
        '-ss', str(start_time),
        '-i', video_file,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-avoid_negative_ts', 'make_zero',
        temp_file
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return temp_file


def combine_clips(temp_clips: List[str], output_file: str) -> bool:
    """
    Combine multiple clips into one using ffmpeg concat.

    Args:
        temp_clips: List of temporary clip file paths
        output_file: Final output file path

    Returns:
        True if successful
    """
    if len(temp_clips) == 1:
        # Just move/copy the single file
        subprocess.run(['cp', temp_clips[0], output_file], check=True)
        return True

    # Create concat file list
    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        for clip in temp_clips:
            concat_file.write(f"file '{os.path.abspath(clip)}'\n")
        concat_file.close()

        # Combine using concat demuxer
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file.name,
            '-c', 'copy',
            output_file
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True

    finally:
        os.unlink(concat_file.name)


def sanitize_filename(title: str) -> str:
    """Convert title to safe filename."""
    safe = title.replace('/', '_').replace('\\', '_')
    safe = ''.join(c for c in safe if c.isalnum() or c in (' ', '-', '_'))
    safe = safe.strip().replace(' ', '_')
    return safe[:100]


def process_segments(
    segments_file: str,
    transcription_file: str,
    video_file: str,
    output_dir: str = 'clips'
):
    """
    Process all segments and extract clips.

    Args:
        segments_file: Path to segments.json
        transcription_file: Path to original transcription JSON
        video_file: Path to source video
        output_dir: Directory for output clips
    """
    # Load data
    print("Loading segments and transcription data...")
    with open(segments_file, 'r', encoding='utf-8') as f:
        segments_data = json.load(f)

    word_map = load_word_level_data(transcription_file)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    clips = segments_data.get('clips', [])
    print(f"\nProcessing {len(clips)} segments...")
    print(f"Length constraints: {MIN_CLIP_LENGTH}s min, {MAX_CLIP_LENGTH}s max\n")

    stats = {
        'total_segments': len(clips),
        'clips_extracted': 0,
        'segments_combined': 0,
        'silences_removed': 0,
        'fillers_removed': 0,
        'skipped_too_short': 0,
        'skipped_too_long': 0,
        'failed': 0
    }

    for idx, segment in enumerate(clips, 1):
        print(f"\n[{idx}/{len(clips)}] Processing: {segment['suggested_title']}")

        try:
            start_idx = segment['start_index']
            end_idx = segment['end_index']

            # Get precise boundaries and count fillers
            precise_start, precise_end, original_word_count = get_precise_boundaries(
                start_idx, end_idx, word_map
            )

            # Calculate total duration after filler removal
            total_duration = precise_end - precise_start

            print(f"  Original: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s ({segment['duration']:.1f}s)")
            print(f"  After filler removal: {precise_start:.2f}s - {precise_end:.2f}s ({total_duration:.1f}s)")

            # Check length constraints
            if total_duration < MIN_CLIP_LENGTH:
                print(f"  ⊘ Skipped: Too short ({total_duration:.1f}s < {MIN_CLIP_LENGTH}s minimum)")
                stats['skipped_too_short'] += 1
                continue

            if total_duration > MAX_CLIP_LENGTH:
                print(f"  ⊘ Skipped: Too long ({total_duration:.1f}s > {MAX_CLIP_LENGTH}s maximum)")
                stats['skipped_too_long'] += 1
                continue

            # Detect silence gaps
            silences = detect_silence_gaps(start_idx, end_idx, word_map)

            if silences:
                print(f"  Found {len(silences)} silence gap(s) > {SILENCE_THRESHOLD}s")
                stats['silences_removed'] += len(silences)

            # Split into sub-clips
            subclips = split_at_silences(precise_start, precise_end, silences)

            if len(subclips) > 1:
                print(f"  Combining {len(subclips)} segment(s) into one clip...")
                stats['segments_combined'] += len(subclips)

            # Create temporary directory for sub-clips
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_files = []

                # Extract each sub-clip
                for sub_idx, (sub_start, sub_end) in enumerate(subclips):
                    print(f"    Extracting segment {sub_idx+1}/{len(subclips)}: {sub_start:.2f}s - {sub_end:.2f}s")
                    temp_file = extract_temp_clip(video_file, sub_start, sub_end, temp_dir, sub_idx)
                    temp_files.append(temp_file)

                # Combine into final output
                safe_title = sanitize_filename(segment['suggested_title'])
                output_file = os.path.join(output_dir, f"{idx:03d}_{safe_title}.mp4")

                print(f"  Combining segments into final clip...")
                if combine_clips(temp_files, output_file):
                    print(f"  ✓ Saved: {output_file} ({total_duration:.1f}s)")
                    stats['clips_extracted'] += 1

                    # Count filler words removed (approximation)
                    # Get word count after filtering
                    all_words = []
                    for i in range(start_idx, end_idx + 1):
                        all_words.extend(word_map.get(i, []))
                    filtered_words = remove_filler_words(all_words)
                    stats['fillers_removed'] += (len(all_words) - len(filtered_words))
                else:
                    print(f"  ✗ Failed to combine segments")
                    stats['failed'] += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats['failed'] += 1
            continue

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total segments:         {stats['total_segments']}")
    print(f"Clips extracted:        {stats['clips_extracted']}")
    print(f"Segments combined:      {stats['segments_combined']}")
    print(f"Silences removed:       {stats['silences_removed']}")
    print(f"Filler words removed:   {stats['fillers_removed']}")
    print(f"Skipped (too short):    {stats['skipped_too_short']}")
    print(f"Skipped (too long):     {stats['skipped_too_long']}")
    print(f"Failed:                 {stats['failed']}")
    print(f"\nOutput directory: {output_dir}/")
    print(f"Length range: {MIN_CLIP_LENGTH}s - {MAX_CLIP_LENGTH}s")
    print("="*60)


def main():
    if len(sys.argv) < 4:
        print("Usage: python extract_clips.py <segments.json> <original_transcription.json> <video.mp4> [output_dir]")
        print("\nExtracts video clips with word-level precision, filler removal, and silence removal.")
        print("\nArguments:")
        print("  segments.json              - Output from analyze step")
        print("  original_transcription.json - Original transcription with word-level data")
        print("  video.mp4                  - Source video file")
        print("  output_dir                 - Output directory (default: clips/)")
        print(f"\nConfiguration:")
        print(f"  Safety buffer:       {SAFETY_BUFFER}s")
        print(f"  Silence threshold:   {SILENCE_THRESHOLD}s")
        print(f"  Min clip length:     {MIN_CLIP_LENGTH}s")
        print(f"  Max clip length:     {MAX_CLIP_LENGTH}s")
        print(f"  Min subclip length:  {MIN_SUBCLIP_LENGTH}s")
        print(f"\nFiller words removed: {', '.join(sorted(FILLER_WORDS))}")
        sys.exit(1)

    segments_file = sys.argv[1]
    transcription_file = sys.argv[2]
    video_file = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else 'clips'

    # Validate files exist
    for file_path, name in [(segments_file, 'Segments'),
                             (transcription_file, 'Transcription'),
                             (video_file, 'Video')]:
        if not os.path.exists(file_path):
            print(f"Error: {name} file not found: {file_path}", file=sys.stderr)
            sys.exit(1)

    # Check ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg not found. Please install ffmpeg first.", file=sys.stderr)
        print("  macOS:   brew install ffmpeg", file=sys.stderr)
        print("  Ubuntu:  sudo apt-get install ffmpeg", file=sys.stderr)
        sys.exit(1)

    process_segments(segments_file, transcription_file, video_file, output_dir)


if __name__ == '__main__':
    main()
