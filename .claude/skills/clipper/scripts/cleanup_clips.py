#!/usr/bin/env python3
"""
Post-processing script to clean up extracted clips.

This is Phase 3 of the extraction pipeline:
- Phase 1: Analysis (identify coherent segments)
- Phase 2: Extraction (extract complete sentences)
- Phase 3: Cleanup (remove silences and filler words) ← THIS SCRIPT

Features:
- Removes filler words (um, uh, ah, like, etc.)
- Removes silences greater than threshold
- Combines remaining parts into clean clips
- Preserves coherent sentence structure from Phase 2

Usage:
    python cleanup_clips.py segments.json transcription.json clips/ [output_dir]
"""

import json
import sys
import os
import subprocess
import tempfile
from typing import List, Dict, Any, Tuple


# Configuration
SAFETY_BUFFER = 0.1       # seconds to add before/after cuts
SILENCE_THRESHOLD = 0.25  # minimum gap to consider silence (seconds)
MIN_SEGMENT_LENGTH = 0.3  # minimum segment length to keep (seconds)

# Filler words to remove (lowercase)
FILLER_WORDS = {
    'um', 'uh', 'uh,', 'um,', 'umm', 'uhh', 'umm,', 'uhh,',
    'ah', 'ah,', 'ahh', 'ahh,',
    'er', 'er,', 'err', 'err,',
    'hmm', 'hmm,', 'hm', 'hm,', 'mm', 'mm,', 'mmm', 'mmm,',
    'like,',  # Only "like," with comma (filler usage)
    'you know,', 'you know',
    'i mean,', 'i mean',
    'sort of,', 'sort of',
    'kind of,', 'kind of',
}


def load_word_level_data(transcription_file: str) -> Dict[int, List[Dict]]:
    """Load word-level timestamps from original transcription."""
    with open(transcription_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    word_map = {}
    for idx, sentence in enumerate(data.get('sentences', [])):
        word_map[idx] = sentence.get('words', [])

    return word_map


def is_filler_word(word: Dict) -> bool:
    """Check if a word is a filler word."""
    text = word.get('word', '').lower().strip()
    return text in FILLER_WORDS


def get_words_for_segment(
    start_idx: int,
    end_idx: int,
    word_map: Dict[int, List[Dict]]
) -> List[Dict]:
    """Get all words for a segment."""
    all_words = []
    for idx in range(start_idx, end_idx + 1):
        all_words.extend(word_map.get(idx, []))
    return all_words


def identify_cuts(
    words: List[Dict]
) -> Tuple[List[Tuple[float, float]], Dict[str, int]]:
    """
    Identify segments to keep after removing fillers and silences.

    Returns:
        Tuple of (list of (start, end) tuples to keep, stats dict)
    """
    if not words:
        return [], {'fillers_removed': 0, 'silences_removed': 0}

    stats = {'fillers_removed': 0, 'silences_removed': 0}

    # Filter out filler words
    clean_words = []
    for word in words:
        if is_filler_word(word):
            stats['fillers_removed'] += 1
        else:
            clean_words.append(word)

    if not clean_words:
        return [], stats

    # Find silence gaps and create segments
    segments = []
    current_start = clean_words[0]['start']
    current_end = clean_words[0]['end']

    for i in range(1, len(clean_words)):
        prev_end = clean_words[i - 1]['end']
        curr_start = clean_words[i]['start']
        gap = curr_start - prev_end

        if gap > SILENCE_THRESHOLD:
            # End current segment, start new one
            segments.append((current_start, current_end))
            current_start = curr_start
            stats['silences_removed'] += 1

        current_end = clean_words[i]['end']

    # Add final segment
    segments.append((current_start, current_end))

    # Filter out segments that are too short
    filtered_segments = []
    for start, end in segments:
        if (end - start) >= MIN_SEGMENT_LENGTH:
            # Add safety buffer
            buffered_start = max(0, start - SAFETY_BUFFER)
            buffered_end = end + SAFETY_BUFFER
            filtered_segments.append((buffered_start, buffered_end))

    return filtered_segments, stats


def extract_segment(
    video_file: str,
    start_time: float,
    end_time: float,
    output_file: str
) -> bool:
    """Extract a single segment from video."""
    duration = end_time - start_time

    cmd = [
        'ffmpeg', '-y',
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


def combine_segments(segment_files: List[str], output_file: str) -> bool:
    """Combine multiple segments into one clip."""
    if len(segment_files) == 1:
        subprocess.run(['cp', segment_files[0], output_file], check=True)
        return True

    # Create concat file
    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        for seg in segment_files:
            concat_file.write(f"file '{os.path.abspath(seg)}'\n")
        concat_file.close()

        cmd = [
            'ffmpeg', '-y',
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


def get_clip_info(clip_file: str) -> Dict[str, Any]:
    """Get duration and other info from a clip file."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        clip_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return {
            'duration': float(data['format'].get('duration', 0)),
            'size': int(data['format'].get('size', 0))
        }
    except:
        return {'duration': 0, 'size': 0}


def cleanup_clip(
    clip_file: str,
    segment: Dict[str, Any],
    word_map: Dict[int, List[Dict]],
    video_file: str,
    output_file: str
) -> Dict[str, Any]:
    """
    Clean up a single clip by removing fillers and silences.

    Args:
        clip_file: Path to the extracted clip (for reference/comparison)
        segment: Segment data from segments.json
        word_map: Word-level timestamps
        video_file: Original source video
        output_file: Where to save cleaned clip

    Returns:
        Stats dictionary
    """
    start_idx = segment['start_index']
    end_idx = segment['end_index']

    # Get words for this segment
    words = get_words_for_segment(start_idx, end_idx, word_map)

    # Identify what to keep
    segments_to_keep, stats = identify_cuts(words)

    if not segments_to_keep:
        return {'success': False, 'error': 'No content left after cleanup', **stats}

    # Get original clip info
    original_info = get_clip_info(clip_file)

    with tempfile.TemporaryDirectory() as temp_dir:
        segment_files = []

        # Extract each segment
        for i, (start, end) in enumerate(segments_to_keep):
            temp_file = os.path.join(temp_dir, f"seg_{i:03d}.mp4")
            if extract_segment(video_file, start, end, temp_file):
                segment_files.append(temp_file)

        if not segment_files:
            return {'success': False, 'error': 'Failed to extract segments', **stats}

        # Combine into output
        if combine_segments(segment_files, output_file):
            cleaned_info = get_clip_info(output_file)

            return {
                'success': True,
                'segments_kept': len(segments_to_keep),
                'original_duration': original_info['duration'],
                'cleaned_duration': cleaned_info['duration'],
                'time_saved': original_info['duration'] - cleaned_info['duration'],
                **stats
            }
        else:
            return {'success': False, 'error': 'Failed to combine segments', **stats}


def process_clips(
    segments_file: str,
    transcription_file: str,
    video_file: str,
    clips_dir: str,
    output_dir: str = None
):
    """
    Process all clips in a directory and clean them up.

    Args:
        segments_file: Path to segments.json
        transcription_file: Path to original transcription
        video_file: Path to original source video
        clips_dir: Directory containing extracted clips
        output_dir: Output directory (default: clips_dir/cleaned/)
    """
    if output_dir is None:
        output_dir = os.path.join(clips_dir, 'cleaned')

    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print("Loading segments and transcription data...")
    with open(segments_file, 'r', encoding='utf-8') as f:
        segments_data = json.load(f)

    word_map = load_word_level_data(transcription_file)

    clips = segments_data.get('clips', [])

    # Find matching clip files
    clip_files = sorted([f for f in os.listdir(clips_dir) if f.endswith('.mp4') and not f.startswith('comp_')])

    print(f"\nFound {len(clip_files)} clips to process")
    print(f"Source video: {video_file}")
    print(f"Output directory: {output_dir}/\n")

    total_stats = {
        'clips_processed': 0,
        'clips_cleaned': 0,
        'total_fillers_removed': 0,
        'total_silences_removed': 0,
        'total_time_saved': 0.0,
        'failed': 0
    }

    for clip_file in clip_files:
        # Extract clip index from filename (e.g., "001_Title.mp4" -> 0)
        try:
            idx = int(clip_file.split('_')[0]) - 1
            if idx < 0 or idx >= len(clips):
                print(f"  ⊘ Skipping {clip_file}: index out of range")
                continue
        except ValueError:
            print(f"  ⊘ Skipping {clip_file}: can't parse index")
            continue

        segment = clips[idx]
        clip_path = os.path.join(clips_dir, clip_file)
        output_path = os.path.join(output_dir, clip_file)

        print(f"[{idx + 1}/{len(clips)}] Processing: {segment['suggested_title'][:50]}...")

        result = cleanup_clip(clip_path, segment, word_map, video_file, output_path)

        if result['success']:
            print(f"  ✓ Cleaned: {result['fillers_removed']} fillers, {result['silences_removed']} silences removed")
            print(f"    Duration: {result['original_duration']:.1f}s → {result['cleaned_duration']:.1f}s ({result['time_saved']:.1f}s saved)")

            total_stats['clips_cleaned'] += 1
            total_stats['total_fillers_removed'] += result['fillers_removed']
            total_stats['total_silences_removed'] += result['silences_removed']
            total_stats['total_time_saved'] += result['time_saved']
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
            total_stats['failed'] += 1

        total_stats['clips_processed'] += 1

    # Print summary
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Clips processed:      {total_stats['clips_processed']}")
    print(f"Clips cleaned:        {total_stats['clips_cleaned']}")
    print(f"Filler words removed: {total_stats['total_fillers_removed']}")
    print(f"Silences removed:     {total_stats['total_silences_removed']}")
    print(f"Total time saved:     {total_stats['total_time_saved']:.1f}s")
    print(f"Failed:               {total_stats['failed']}")
    print(f"\nOutput directory: {output_dir}/")
    print("=" * 60)


def main():
    if len(sys.argv) < 5:
        print("Usage: python cleanup_clips.py <segments.json> <transcription.json> <video.mp4> <clips_dir> [output_dir]")
        print("\nPost-processes extracted clips to remove fillers and silences.")
        print("\nThis is Phase 3 of the pipeline:")
        print("  Phase 1: Analysis (identify coherent segments)")
        print("  Phase 2: Extraction (extract complete sentences)")
        print("  Phase 3: Cleanup (this script)")
        print("\nArguments:")
        print("  segments.json      - Segment definitions from analysis")
        print("  transcription.json - Original transcription with word-level data")
        print("  video.mp4          - Original source video file")
        print("  clips_dir          - Directory containing extracted clips")
        print("  output_dir         - Output directory (default: clips_dir/cleaned/)")
        print(f"\nConfiguration:")
        print(f"  Safety buffer:      {SAFETY_BUFFER}s")
        print(f"  Silence threshold:  {SILENCE_THRESHOLD}s")
        print(f"  Min segment length: {MIN_SEGMENT_LENGTH}s")
        print(f"\nFiller words: {', '.join(sorted(FILLER_WORDS))}")
        sys.exit(1)

    segments_file = sys.argv[1]
    transcription_file = sys.argv[2]
    video_file = sys.argv[3]
    clips_dir = sys.argv[4]
    output_dir = sys.argv[5] if len(sys.argv) > 5 else None

    # Validate files/directories exist
    for path, name in [(segments_file, 'Segments'),
                       (transcription_file, 'Transcription'),
                       (video_file, 'Video'),
                       (clips_dir, 'Clips directory')]:
        if not os.path.exists(path):
            print(f"Error: {name} not found: {path}", file=sys.stderr)
            sys.exit(1)

    process_clips(segments_file, transcription_file, video_file, clips_dir, output_dir)


if __name__ == '__main__':
    main()
