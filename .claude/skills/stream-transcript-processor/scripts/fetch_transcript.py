#!/usr/bin/env python3
"""
Fetch auto-generated transcript from Twitch VOD or YouTube video.

This script uses yt-dlp to download auto-generated captions and converts
them to a timestamped transcript format compatible with the clipper skill.

Usage:
    python fetch_transcript.py <URL> [output_path]

Examples:
    python fetch_transcript.py https://www.youtube.com/watch?v=abc123
    python fetch_transcript.py https://twitch.tv/videos/123456 transcript.txt
"""

import subprocess
import sys
import re
import json
from pathlib import Path
from typing import Optional


def timestamp_to_seconds(ts: str) -> float:
    """Convert HH:MM:SS.mmm to seconds."""
    parts = ts.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    else:
        return float(ts)


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_vtt(vtt_path: Path) -> list[dict]:
    """
    Parse VTT file to list of transcript entries.

    Returns list of dicts with:
        - timestamp: HH:MM:SS format
        - seconds: float seconds from start
        - text: cleaned text content
    """
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    entries = []
    current_timestamp = None
    current_seconds = 0.0

    # Match timestamp pattern: 00:00:00.000 --> 00:00:05.000
    timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2})[.,]\d{3}\s*-->')

    for line in lines:
        # Check for timestamp line
        match = timestamp_pattern.search(line)
        if match:
            current_timestamp = match.group(1)
            current_seconds = timestamp_to_seconds(current_timestamp)
        elif line.strip() and not line.startswith('WEBVTT') and '-->' not in line and not line.strip().isdigit():
            # Clean text line: remove VTT tags and duplicate entries
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            if clean_line and current_timestamp:
                # Avoid duplicate consecutive entries
                if not entries or entries[-1]['text'] != clean_line:
                    entries.append({
                        'timestamp': current_timestamp,
                        'seconds': current_seconds,
                        'text': clean_line
                    })

    return entries


def merge_entries(entries: list[dict], merge_window: float = 5.0) -> list[dict]:
    """
    Merge transcript entries that are close together into sentences.

    Args:
        entries: List of transcript entries
        merge_window: Maximum gap in seconds to merge entries

    Returns:
        List of merged entries with combined text
    """
    if not entries:
        return []

    merged = []
    current = {
        'timestamp': entries[0]['timestamp'],
        'seconds': entries[0]['seconds'],
        'text': entries[0]['text']
    }

    for entry in entries[1:]:
        gap = entry['seconds'] - (current['seconds'] + 2.0)  # Assume ~2s per phrase

        # Merge if close together and text doesn't end with punctuation
        if gap < merge_window and not current['text'].rstrip().endswith(('.', '!', '?')):
            # Avoid duplicate text
            if entry['text'] not in current['text']:
                current['text'] += ' ' + entry['text']
        else:
            merged.append(current)
            current = {
                'timestamp': entry['timestamp'],
                'seconds': entry['seconds'],
                'text': entry['text']
            }

    merged.append(current)
    return merged


def fetch_transcript(url: str, output_path: str = "transcript.txt") -> str:
    """
    Fetch auto-generated captions from YouTube/Twitch.

    Args:
        url: Video URL (YouTube or Twitch)
        output_path: Output file path (default: transcript.txt)

    Returns:
        Status message
    """
    temp_base = "temp_transcript_fetch"

    try:
        # Download subtitles using yt-dlp
        result = subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--sub-format", "vtt",
            "-o", temp_base,
            url
        ], capture_output=True, text=True, check=True)

        # Find the downloaded subtitle file
        vtt_files = list(Path(".").glob(f"{temp_base}*.vtt"))

        if not vtt_files:
            # Try with different language variants
            for lang in ['en-US', 'en-GB', 'en-orig']:
                subprocess.run([
                    "yt-dlp",
                    "--write-auto-sub",
                    "--sub-lang", lang,
                    "--skip-download",
                    "--sub-format", "vtt",
                    "-o", temp_base,
                    url
                ], capture_output=True, text=True)
                vtt_files = list(Path(".").glob(f"{temp_base}*.vtt"))
                if vtt_files:
                    break

        if not vtt_files:
            return "ERROR: No transcript found. Video may not have auto-generated captions."

        # Parse VTT to transcript entries
        entries = parse_vtt(vtt_files[0])

        if not entries:
            return "ERROR: Transcript file was empty or could not be parsed."

        # Merge close entries into more complete sentences
        merged = merge_entries(entries)

        # Write timestamped transcript
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in merged:
                f.write(f"[{entry['timestamp']}] {entry['text']}\n")

        # Also create a JSON version for programmatic access
        json_path = Path(output_path).with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'total_entries': len(merged),
                'duration_seconds': merged[-1]['seconds'] if merged else 0,
                'entries': merged
            }, f, indent=2)

        # Cleanup temp files
        for vtt_file in vtt_files:
            try:
                vtt_file.unlink()
            except Exception:
                pass

        duration = seconds_to_timestamp(merged[-1]['seconds']) if merged else "00:00:00"
        return f"SUCCESS: Transcript saved to {output_path} ({len(merged)} entries, {duration} duration)"

    except subprocess.CalledProcessError as e:
        return f"ERROR: yt-dlp failed - {e.stderr or str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python fetch_transcript.py <URL> [output_path]")
        sys.exit(1)

    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "transcript.txt"

    result = fetch_transcript(url, output)
    print(result)

    if result.startswith("ERROR"):
        sys.exit(1)


if __name__ == "__main__":
    main()
