#!/usr/bin/env python3
"""
Download videos from YouTube, TikTok, Instagram, X, and 1500+ other sites using yt-dlp.

Usage:
    python download_video.py "https://youtube.com/watch?v=xxx" --output media/videos/
    python download_video.py url1 url2 url3 --max-duration 300

Requires yt-dlp to be installed:
    brew install yt-dlp   # macOS
    pip install yt-dlp    # via pip
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def check_ytdlp_installed() -> bool:
    """Check if yt-dlp is installed and accessible."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_video_info(url: str) -> dict:
    """Get video metadata without downloading."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                url
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"error": "Timeout getting video info"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse video info"}
    except Exception as e:
        return {"error": str(e)}


def sanitize_filename(title: str, max_length: int = 50) -> str:
    """Create a safe filename from video title."""
    # Remove/replace unsafe characters
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'\s+', '_', safe)
    safe = safe[:max_length]
    return safe.strip('_')


def download_video(url: str, output_dir: Path, max_duration: int = 300) -> dict:
    """
    Download a video using yt-dlp.

    Returns dict with status and details.
    """
    result = {
        "url": url,
        "success": False,
        "path": None,
        "title": None,
        "duration": None,
        "platform": None,
        "error": None
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    # First, get video info to check duration
    info = get_video_info(url)

    if "error" in info:
        result["error"] = info["error"]
        return result

    duration = info.get("duration", 0)
    title = info.get("title", "video")
    platform = info.get("extractor", "unknown")
    video_id = info.get("id", "unknown")

    result["title"] = title
    result["duration"] = duration
    result["platform"] = platform

    # Check duration limit
    if duration and duration > max_duration:
        result["error"] = f"Video too long: {duration}s > {max_duration}s limit"
        return result

    # Generate output filename
    safe_title = sanitize_filename(title)
    output_template = str(output_dir / f"{platform}_{video_id}_{safe_title}.%(ext)s")

    try:
        # Download with yt-dlp
        cmd = [
            "yt-dlp",
            # Format selection: best quality up to 1080p
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            # Merge to mp4
            "--merge-output-format", "mp4",
            # Output template
            "-o", output_template,
            # Embed metadata
            "--embed-metadata",
            # No playlist (single video only)
            "--no-playlist",
            # Quiet but show errors
            "--quiet",
            "--no-warnings",
            # The URL
            url
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for download
        )

        if proc.returncode == 0:
            # Find the downloaded file
            expected_path = output_dir / f"{platform}_{video_id}_{safe_title}.mp4"

            # yt-dlp might use different extension, search for it
            possible_files = list(output_dir.glob(f"{platform}_{video_id}_{safe_title}.*"))

            if possible_files:
                result["success"] = True
                result["path"] = str(possible_files[0])
            else:
                # Try to find any recent file
                result["success"] = True
                result["path"] = str(expected_path)
        else:
            result["error"] = proc.stderr or "Download failed"

    except subprocess.TimeoutExpired:
        result["error"] = "Download timed out (>10 minutes)"
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Download videos using yt-dlp (YouTube, TikTok, Instagram, X, etc.)"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="Video URLs to download"
    )
    parser.add_argument(
        "--output", "-o",
        default="media/videos/",
        help="Output directory (default: media/videos/)"
    )
    parser.add_argument(
        "--max-duration", "-d",
        type=int,
        default=300,
        help="Skip videos longer than N seconds (default: 300)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Check yt-dlp is installed
    if not check_ytdlp_installed():
        print("Error: yt-dlp is not installed", file=sys.stderr)
        print("Install with: brew install yt-dlp  OR  pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    results = []
    success_count = 0

    for url in args.urls:
        print(f"Downloading: {url}", file=sys.stderr)
        result = download_video(url, output_dir, args.max_duration)
        results.append(result)

        if result["success"]:
            success_count += 1
            duration_str = f"{result['duration']}s" if result['duration'] else "unknown duration"
            print(f"✓ {result['platform']}: {result['title']} ({duration_str})", file=sys.stderr)
            print(f"  → {result['path']}", file=sys.stderr)
        else:
            print(f"✗ {url}: {result['error']}", file=sys.stderr)

    # Summary
    print(f"\nDownloaded {success_count}/{len(args.urls)} videos", file=sys.stderr)

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(0 if success_count == len(args.urls) else 1)


if __name__ == "__main__":
    main()
