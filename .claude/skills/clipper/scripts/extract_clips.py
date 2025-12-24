#!/usr/bin/env python3
"""
Extract video clips from segments with word-level precision and silence removal.

Features:
- Uses word-level timestamps for precise clip boundaries
- Adds 0.1s safety buffer to avoid clipping inside words
- Removes silences greater than 0.4s duration
- Splits segments at long silence points
- Generates clips using ffmpeg

Usage:
    python extract_clips.py segments.json original_transcription.json video.mp4 [output_dir]
"""

import json
import sys
import os
import subprocess
from typing import List, Dict, Any, Tuple


# Configuration
SAFETY_BUFFER = 0.1  # seconds to add before/after words
SILENCE_THRESHOLD = 0.4  # seconds - gaps larger than this are considered silence
MIN_SUBCLIP_LENGTH = 3.0  # seconds - minimum length for a sub-clip after silence removal


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


def get_precise_boundaries(
    start_idx: int,
    end_idx: int,
    word_map: Dict[int, List[Dict]]
) -> Tuple[float, float]:
    """
    Get precise start and end times using word-level timestamps.

    Args:
        start_idx: Starting sentence index
        end_idx: Ending sentence index
        word_map: Dictionary mapping sentence index to words

    Returns:
        Tuple of (precise_start, precise_end) with safety buffer applied
    """
    # Get first word of first sentence
    first_sentence_words = word_map.get(start_idx, [])
    if not first_sentence_words:
        raise ValueError(f"No words found for sentence {start_idx}")

    first_word_start = first_sentence_words[0]['start']

    # Get last word of last sentence
    last_sentence_words = word_map.get(end_idx, [])
    if not last_sentence_words:
        raise ValueError(f"No words found for sentence {end_idx}")

    last_word_end = last_sentence_words[-1]['end']

    # Apply safety buffer
    precise_start = max(0, first_word_start - SAFETY_BUFFER)
    precise_end = last_word_end + SAFETY_BUFFER

    return precise_start, precise_end


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

    # Collect all words in the segment
    all_words = []
    for idx in range(start_idx, end_idx + 1):
        all_words.extend(word_map.get(idx, []))

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


def extract_clip_with_ffmpeg(
    video_file: str,
    start_time: float,
    end_time: float,
    output_file: str
) -> bool:
    """
    Extract a clip from video using ffmpeg.

    Args:
        video_file: Path to input video
        start_time: Start time in seconds
        end_time: End time in seconds
        output_file: Path to output clip

    Returns:
        True if successful, False otherwise
    """
    duration = end_time - start_time

    # Use ffmpeg with precise seeking and re-encoding for accuracy
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file
        '-ss', str(start_time),  # Seek to start
        '-i', video_file,  # Input file
        '-t', str(duration),  # Duration
        '-c:v', 'libx264',  # Re-encode video for precision
        '-c:a', 'aac',  # Re-encode audio
        '-strict', 'experimental',
        '-avoid_negative_ts', 'make_zero',  # Handle timestamp issues
        output_file
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}", file=sys.stderr)
        return False


def sanitize_filename(title: str) -> str:
    """Convert title to safe filename."""
    # Remove or replace unsafe characters
    safe = title.replace('/', '_').replace('\\', '_')
    safe = ''.join(c for c in safe if c.isalnum() or c in (' ', '-', '_'))
    safe = safe.strip().replace(' ', '_')
    return safe[:100]  # Limit length


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

    stats = {
        'total_segments': len(clips),
        'clips_extracted': 0,
        'subclips_created': 0,
        'silences_removed': 0,
        'failed': 0
    }

    for idx, segment in enumerate(clips, 1):
        print(f"\n[{idx}/{len(clips)}] Processing: {segment['suggested_title']}")

        try:
            # Get precise boundaries using word-level data
            start_idx = segment['start_index']
            end_idx = segment['end_index']

            precise_start, precise_end = get_precise_boundaries(
                start_idx, end_idx, word_map
            )

            print(f"  Original: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
            print(f"  Precise:  {precise_start:.2f}s - {precise_end:.2f}s")

            # Detect silence gaps
            silences = detect_silence_gaps(start_idx, end_idx, word_map)

            if silences:
                print(f"  Found {len(silences)} silence gap(s) > {SILENCE_THRESHOLD}s")
                stats['silences_removed'] += len(silences)

                # Split into sub-clips
                subclips = split_at_silences(precise_start, precise_end, silences)
                print(f"  Split into {len(subclips)} sub-clip(s)")

                # Extract each sub-clip
                for sub_idx, (sub_start, sub_end) in enumerate(subclips):
                    safe_title = sanitize_filename(segment['suggested_title'])

                    if len(subclips) > 1:
                        output_file = os.path.join(
                            output_dir,
                            f"{idx:03d}_{safe_title}_part{sub_idx+1}.mp4"
                        )
                    else:
                        output_file = os.path.join(
                            output_dir,
                            f"{idx:03d}_{safe_title}.mp4"
                        )

                    print(f"    Extracting part {sub_idx+1}: {sub_start:.2f}s - {sub_end:.2f}s")

                    if extract_clip_with_ffmpeg(video_file, sub_start, sub_end, output_file):
                        print(f"    ✓ Saved: {output_file}")
                        stats['subclips_created'] += 1
                    else:
                        print(f"    ✗ Failed to extract sub-clip")
                        stats['failed'] += 1

                stats['clips_extracted'] += 1
            else:
                # No silences, extract as single clip
                safe_title = sanitize_filename(segment['suggested_title'])
                output_file = os.path.join(output_dir, f"{idx:03d}_{safe_title}.mp4")

                print(f"  No silences detected")

                if extract_clip_with_ffmpeg(video_file, precise_start, precise_end, output_file):
                    print(f"  ✓ Saved: {output_file}")
                    stats['clips_extracted'] += 1
                    stats['subclips_created'] += 1
                else:
                    print(f"  ✗ Failed to extract clip")
                    stats['failed'] += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats['failed'] += 1
            continue

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total segments:       {stats['total_segments']}")
    print(f"Clips extracted:      {stats['clips_extracted']}")
    print(f"Sub-clips created:    {stats['subclips_created']}")
    print(f"Silences removed:     {stats['silences_removed']}")
    print(f"Failed:               {stats['failed']}")
    print(f"\nOutput directory: {output_dir}/")
    print("="*60)


def main():
    if len(sys.argv) < 4:
        print("Usage: python extract_clips.py <segments.json> <original_transcription.json> <video.mp4> [output_dir]")
        print("\nExtracts video clips with word-level precision and silence removal.")
        print("\nArguments:")
        print("  segments.json              - Output from analyze step")
        print("  original_transcription.json - Original transcription with word-level data")
        print("  video.mp4                  - Source video file")
        print("  output_dir                 - Output directory (default: clips/)")
        print(f"\nConfiguration:")
        print(f"  Safety buffer:       {SAFETY_BUFFER}s")
        print(f"  Silence threshold:   {SILENCE_THRESHOLD}s")
        print(f"  Min subclip length:  {MIN_SUBCLIP_LENGTH}s")
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
