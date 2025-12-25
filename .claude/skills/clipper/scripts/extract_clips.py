#!/usr/bin/env python3
"""
Extract video clips from segments with word-level precision.

Features:
- Uses word-level timestamps for precise clip boundaries
- Adds 0.1s safety buffer to avoid clipping inside words
- Extracts complete, coherent sentences as identified during analysis
- Enforces length constraints (60s min, 360s max)
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
MIN_CLIP_LENGTH = 60.0  # seconds - minimum total clip length (1 minute)
MAX_CLIP_LENGTH = 360.0  # seconds - maximum total clip length (6 minutes)


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

    Simply extracts from first word to last word with safety buffer.
    No filler removal, no silence detection - just coherent sentence boundaries.

    Args:
        start_idx: Starting sentence index
        end_idx: Ending sentence index
        word_map: Dictionary mapping sentence index to words

    Returns:
        Tuple of (precise_start, precise_end)
    """
    # Collect all words in the segment
    all_words = []
    for idx in range(start_idx, end_idx + 1):
        all_words.extend(word_map.get(idx, []))

    if not all_words:
        raise ValueError(f"No words found for sentences {start_idx}-{end_idx}")

    # Get first and last word timestamps
    first_word_start = all_words[0]['start']
    last_word_end = all_words[-1]['end']

    # Apply safety buffer
    precise_start = max(0, first_word_start - SAFETY_BUFFER)
    precise_end = last_word_end + SAFETY_BUFFER

    return precise_start, precise_end


def extract_clip(
    video_file: str,
    start_time: float,
    end_time: float,
    output_file: str
) -> bool:
    """
    Extract a single coherent clip from the video.

    No silence removal, no filler removal - just the complete sentences
    as identified during analysis.

    Args:
        video_file: Source video file
        start_time: Start time in seconds
        end_time: End time in seconds
        output_file: Output file path

    Returns:
        True if successful, False otherwise
    """
    duration = end_time - start_time

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
        output_file
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


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


def process_compilation(
    compilation: Dict[str, Any],
    clips: List[Dict],
    word_map: Dict[int, List[Dict]],
    video_file: str,
    output_dir: str
) -> Dict[str, Any]:
    """
    Process a compilation by combining multiple coherent segments.

    Each segment is extracted as-is (complete sentences), then combined.
    No silence removal, no filler removal - preserves natural speech.

    Args:
        compilation: Compilation definition from segments.json
        clips: Full clips array to reference segments
        word_map: Word-level timestamps
        video_file: Source video file
        output_dir: Output directory

    Returns:
        Stats dictionary with extraction results
    """
    comp_id = compilation['id']
    title = compilation['title']
    segment_indices = compilation['segment_indices']

    print(f"\n{'='*60}")
    print(f"Processing compilation: {title}")
    print(f"  Topic: {compilation['topic']}")
    print(f"  Segments: {len(segment_indices)}")
    print(f"{'='*60}")

    stats = {
        'segments_processed': 0,
        'failed': False
    }

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_files = []

            # Extract each coherent segment
            for seg_num, seg_idx in enumerate(segment_indices, 1):
                segment = clips[seg_idx]
                print(f"\n  [{seg_num}/{len(segment_indices)}] {segment['suggested_title'][:50]}...")

                start_idx = segment['start_index']
                end_idx = segment['end_index']

                # Get precise boundaries
                precise_start, precise_end = get_precise_boundaries(
                    start_idx, end_idx, word_map
                )

                duration = precise_end - precise_start
                print(f"    Duration: {duration:.1f}s (sentences {start_idx}-{end_idx})")

                # Extract this coherent segment
                temp_file = os.path.join(temp_dir, f"seg_{seg_num:03d}.mp4")
                extract_clip(video_file, precise_start, precise_end, temp_file)
                temp_files.append(temp_file)
                stats['segments_processed'] += 1

            # Combine all segments into one compilation
            safe_title = sanitize_filename(title)
            output_file = os.path.join(output_dir, f"{comp_id}_{safe_title}.mp4")

            print(f"\n  Combining {len(temp_files)} segment(s) into compilation...")
            if combine_clips(temp_files, output_file):
                total_duration = compilation['talking_duration']
                print(f"  ✓ Saved: {output_file} ({total_duration:.1f}s)")
                return stats
            else:
                print(f"  ✗ Failed to combine segments")
                stats['failed'] = True
                return stats

    except Exception as e:
        print(f"  ✗ Error processing compilation: {e}")
        stats['failed'] = True
        return stats


def process_segments(
    segments_file: str,
    transcription_file: str,
    video_file: str,
    output_dir: str = 'clips'
):
    """
    Process all segments and extract coherent clips.

    Each clip is extracted exactly as identified during analysis - complete,
    coherent sentences with no post-processing or splitting.

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
    print(f"\nProcessing {len(clips)} coherent segments...")
    print(f"Length constraints: {MIN_CLIP_LENGTH}s min, {MAX_CLIP_LENGTH}s max\n")

    stats = {
        'total_segments': len(clips),
        'clips_extracted': 0,
        'skipped_too_short': 0,
        'skipped_too_long': 0,
        'failed': 0
    }

    for idx, segment in enumerate(clips, 1):
        print(f"\n[{idx}/{len(clips)}] Processing: {segment['suggested_title']}")

        try:
            start_idx = segment['start_index']
            end_idx = segment['end_index']

            # Get precise boundaries (first word to last word with buffer)
            precise_start, precise_end = get_precise_boundaries(
                start_idx, end_idx, word_map
            )

            # Calculate duration
            duration = precise_end - precise_start

            print(f"  Sentences: {start_idx} - {end_idx}")
            print(f"  Time: {precise_start:.2f}s - {precise_end:.2f}s ({duration:.1f}s)")

            # Check length constraints
            if duration < MIN_CLIP_LENGTH:
                print(f"  ⊘ Skipped: Too short ({duration:.1f}s < {MIN_CLIP_LENGTH}s minimum)")
                stats['skipped_too_short'] += 1
                continue

            if duration > MAX_CLIP_LENGTH:
                print(f"  ⊘ Skipped: Too long ({duration:.1f}s > {MAX_CLIP_LENGTH}s maximum)")
                stats['skipped_too_long'] += 1
                continue

            # Extract the coherent clip
            safe_title = sanitize_filename(segment['suggested_title'])
            output_file = os.path.join(output_dir, f"{idx:03d}_{safe_title}.mp4")

            if extract_clip(video_file, precise_start, precise_end, output_file):
                print(f"  ✓ Saved: {output_file} ({duration:.1f}s)")
                stats['clips_extracted'] += 1
            else:
                print(f"  ✗ Failed to extract clip")
                stats['failed'] += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats['failed'] += 1
            continue

    # Process compilations if present
    compilations = segments_data.get('compilations', [])
    compilation_stats = {
        'total_compilations': len(compilations),
        'compilations_created': 0,
        'compilation_segments': 0,
        'compilation_failed': 0
    }

    if compilations:
        print(f"\n\n{'='*60}")
        print(f"PROCESSING COMPILATIONS")
        print(f"{'='*60}")
        print(f"Found {len(compilations)} compilation(s) to create\n")

        for comp in compilations:
            comp_stats = process_compilation(
                comp, clips, word_map, video_file, output_dir
            )
            if not comp_stats['failed']:
                compilation_stats['compilations_created'] += 1
                compilation_stats['compilation_segments'] += comp_stats['segments_processed']
            else:
                compilation_stats['compilation_failed'] += 1

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Individual Clips:")
    print(f"  Total segments:         {stats['total_segments']}")
    print(f"  Clips extracted:        {stats['clips_extracted']}")
    print(f"  Skipped (too short):    {stats['skipped_too_short']}")
    print(f"  Skipped (too long):     {stats['skipped_too_long']}")
    print(f"  Failed:                 {stats['failed']}")

    if compilations:
        print(f"\nCompilations:")
        print(f"  Total compilations:     {compilation_stats['total_compilations']}")
        print(f"  Compilations created:   {compilation_stats['compilations_created']}")
        print(f"  Segments combined:      {compilation_stats['compilation_segments']}")
        print(f"  Failed:                 {compilation_stats['compilation_failed']}")

    print(f"\nOutput directory: {output_dir}/")
    print(f"Individual clip length range: {MIN_CLIP_LENGTH}s - {MAX_CLIP_LENGTH}s")
    if compilations:
        print(f"Compilations can exceed max length (multi-segment)")
    print("="*60)


def main():
    if len(sys.argv) < 4:
        print("Usage: python extract_clips.py <segments.json> <original_transcription.json> <video.mp4> [output_dir]")
        print("\nExtracts coherent video clips with word-level precision.")
        print("\nArguments:")
        print("  segments.json              - Output from analyze step")
        print("  original_transcription.json - Original transcription with word-level data")
        print("  video.mp4                  - Source video file")
        print("  output_dir                 - Output directory (default: clips/)")
        print(f"\nConfiguration:")
        print(f"  Safety buffer:       {SAFETY_BUFFER}s")
        print(f"  Min clip length:     {MIN_CLIP_LENGTH}s")
        print(f"  Max clip length:     {MAX_CLIP_LENGTH}s")
        print(f"\nExtracts complete, coherent sentences as identified during analysis.")
        print(f"No post-processing - clips are extracted exactly as analyzed.")
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
