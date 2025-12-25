#!/usr/bin/env python3
"""
List YouTube channel videos filtered by date range.

Uses yt-dlp to fetch video metadata from a channel and filters by upload date.

Usage:
    python list_channel_videos.py <channel_url> --start 2024-12-16 --end 2024-12-21
    python list_channel_videos.py <channel_url> --days 7  # last 7 days
"""

import subprocess
import json
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional


DEFAULT_CHANNEL = "https://www.youtube.com/@techfren"


def parse_date(date_str: str) -> datetime:
    """Parse various date formats."""
    formats = [
        "%Y-%m-%d",      # 2024-12-16
        "%Y%m%d",        # 20241216
        "%b %d",         # Dec 16
        "%B %d",         # December 16
        "%b %d %Y",      # Dec 16 2024
        "%B %d %Y",      # December 16 2024
        "%m/%d/%Y",      # 12/16/2024
        "%m-%d-%Y",      # 12-16-2024
    ]

    # Handle relative dates
    date_lower = date_str.lower().strip()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if date_lower == "today":
        return today
    elif date_lower == "yesterday":
        return today - timedelta(days=1)

    # Try each format
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str.strip(), fmt)
            # If year not specified, assume current year (or last year if date is in future)
            if parsed.year == 1900:
                parsed = parsed.replace(year=today.year)
                # If the date is in the future, use last year
                if parsed > today + timedelta(days=7):  # Allow 7 days grace
                    parsed = parsed.replace(year=today.year - 1)
            return parsed
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {date_str}")


def get_channel_videos(channel_url: str, max_videos: int = 50, streams_only: bool = True) -> List[Dict]:
    """
    Fetch video metadata from a YouTube channel using yt-dlp.

    Args:
        channel_url: YouTube channel URL
        max_videos: Maximum number of videos to fetch
        streams_only: If True, fetch from /streams tab (VODs). If False, fetch from /videos tab.

    Returns:
        List of video dictionaries with id, title, upload_date, url, duration
    """
    # Determine which tab to fetch from
    tab = "/streams" if streams_only else "/videos"

    # Use yt-dlp to get video list with metadata
    # Note: --skip-download is slower than --flat-playlist but gives us upload dates
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--no-warnings",
        "--ignore-errors",  # Skip members-only or unavailable videos
        "--print", "%(id)s|%(title)s|%(upload_date)s|%(duration)s",
        "--playlist-end", str(max_videos),
        f"{channel_url}{tab}"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't fail on errors (some videos may be members-only)
        )
    except FileNotFoundError:
        print("Error: yt-dlp not found. Install with: brew install yt-dlp", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line or "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) >= 4:
            video_id, title, upload_date, duration = parts[0], parts[1], parts[2], parts[3]

            # Parse upload date (format: YYYYMMDD)
            try:
                if upload_date and upload_date != "NA":
                    parsed_date = datetime.strptime(upload_date, "%Y%m%d")
                else:
                    parsed_date = None
            except ValueError:
                parsed_date = None

            # Parse duration
            try:
                duration_sec = int(duration) if duration and duration != "NA" else None
            except ValueError:
                duration_sec = None

            videos.append({
                "id": video_id,
                "title": title,
                "upload_date": upload_date,
                "upload_datetime": parsed_date,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration_seconds": duration_sec
            })

    return videos


def filter_by_date_range(
    videos: List[Dict],
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    """Filter videos to those within the date range (inclusive)."""
    filtered = []

    # Make end_date inclusive (end of day)
    end_date = end_date.replace(hour=23, minute=59, second=59)

    for video in videos:
        upload_dt = video.get("upload_datetime")
        if upload_dt and start_date <= upload_dt <= end_date:
            filtered.append(video)

    return filtered


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in human readable form."""
    if seconds is None:
        return "unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def main():
    parser = argparse.ArgumentParser(
        description="List YouTube channel videos filtered by date range"
    )
    parser.add_argument(
        "channel",
        nargs="?",
        default=DEFAULT_CHANNEL,
        help=f"YouTube channel URL (default: {DEFAULT_CHANNEL})"
    )
    parser.add_argument(
        "--start", "-s",
        help="Start date (e.g., 2024-12-16, 'Dec 16', 'yesterday')"
    )
    parser.add_argument(
        "--end", "-e",
        help="End date (e.g., 2024-12-21, 'Dec 21', 'today')"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        help="Alternative: get videos from last N days"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=100,
        help="Maximum videos to scan (default: 100)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON instead of human-readable"
    )
    parser.add_argument(
        "--streams",
        action="store_true",
        default=True,
        help="Fetch stream VODs only (default: True)"
    )
    parser.add_argument(
        "--videos",
        action="store_true",
        help="Fetch regular uploads instead of streams"
    )

    args = parser.parse_args()

    # Determine content type
    if args.videos:
        args.streams = False

    # Determine date range
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if args.days:
        start_date = today - timedelta(days=args.days - 1)
        end_date = today
    elif args.start and args.end:
        start_date = parse_date(args.start)
        end_date = parse_date(args.end)
    elif args.start:
        start_date = parse_date(args.start)
        end_date = today
    else:
        # Default: last 7 days
        start_date = today - timedelta(days=6)
        end_date = today

    # Fetch and filter videos
    content_type = "stream VODs" if args.streams else "videos"
    print(f"Fetching {content_type} from {args.channel}...", file=sys.stderr)
    videos = get_channel_videos(args.channel, args.max, streams_only=args.streams)
    print(f"Found {len(videos)} total {content_type}", file=sys.stderr)

    filtered = filter_by_date_range(videos, start_date, end_date)

    # Sort by date (oldest first for processing order)
    filtered.sort(key=lambda v: v.get("upload_date", ""))

    if args.json:
        # JSON output for scripting
        output = {
            "channel": args.channel,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "videos": [
                {
                    "id": v["id"],
                    "title": v["title"],
                    "upload_date": v["upload_date"],
                    "url": v["url"],
                    "duration_seconds": v["duration_seconds"]
                }
                for v in filtered
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\n{content_type.title()} from {start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}:")
        print(f"{'='*60}")

        if not filtered:
            print(f"No {content_type} found in this date range.")
        else:
            for i, video in enumerate(filtered, 1):
                date_str = video.get("upload_date", "unknown")
                if date_str and date_str != "unknown":
                    date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                duration = format_duration(video.get("duration_seconds"))

                print(f"\n{i}. [{date_str}] {video['title']}")
                print(f"   Duration: {duration}")
                print(f"   URL: {video['url']}")

        print(f"\n{'='*60}")
        print(f"Total: {len(filtered)} {content_type}")


if __name__ == "__main__":
    main()
