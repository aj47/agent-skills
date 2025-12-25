#!/usr/bin/env python3
"""
Capture screenshots using Playwright with dimensions matching video clips.

Usage:
    # Auto-detect dimensions from video file
    python capture_screenshot.py https://github.com/aj47/SpeakMCP --video clips/001_Example.mp4

    # Specify dimensions directly
    python capture_screenshot.py https://github.com/aj47/SpeakMCP --width 1080 --height 1920

    # Multiple URLs
    python capture_screenshot.py url1 url2 url3 --video video.mp4 --output media/screenshots/

Default: Portrait 1080x1920 (9:16 ratio for TikTok/Reels/Shorts)
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...", file=sys.stderr)
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright


# Default to portrait (TikTok/Reels/Shorts format)
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920


def get_video_dimensions(video_path: str) -> tuple[int, int]:
    """
    Extract video dimensions using ffprobe.

    Returns (width, height) or defaults if detection fails.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                video_path
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            if streams:
                width = streams[0].get("width", DEFAULT_WIDTH)
                height = streams[0].get("height", DEFAULT_HEIGHT)
                return (width, height)
    except Exception as e:
        print(f"Warning: Could not detect video dimensions: {e}", file=sys.stderr)

    return (DEFAULT_WIDTH, DEFAULT_HEIGHT)


def url_to_filename(url: str) -> str:
    """Convert URL to safe filename."""
    parsed = urlparse(url)
    # Combine domain and path
    name = parsed.netloc + parsed.path
    # Replace unsafe characters
    safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)
    # Remove consecutive underscores and trim
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")[:100]


async def capture_screenshot(
    page,
    url: str,
    output_dir: Path,
    filename: str = None
) -> dict:
    """Capture a screenshot of a URL."""
    result = {
        "url": url,
        "success": False,
        "path": None,
        "error": None
    }

    if not filename:
        filename = url_to_filename(url) + ".png"

    output_path = output_dir / filename

    try:
        print(f"  Navigating to {url}...", file=sys.stderr)
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Try to dismiss common overlays/cookie banners
        dismiss_selectors = [
            "text=Accept",
            "text=Accept all",
            "text=Accept All",
            "text=I agree",
            "text=Got it",
            "text=OK",
            "text=Close",
            "[aria-label='Close']",
            "[aria-label='Dismiss']",
            ".cookie-banner button",
            "[data-testid='cookie-accept']",
            "#onetrust-accept-btn-handler",
        ]

        for selector in dismiss_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=500):
                    await element.click()
                    await page.wait_for_timeout(300)
                    break
            except:
                pass

        # Wait for animations to settle
        await page.wait_for_timeout(1000)

        # Take screenshot (viewport only, not full page - to match video dimensions)
        await page.screenshot(path=str(output_path), full_page=False)

        result["success"] = True
        result["path"] = str(output_path)
        print(f"  ✓ Saved: {output_path}", file=sys.stderr)

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ Failed: {e}", file=sys.stderr)

    return result


async def main(
    urls: list[str],
    output_dir: Path,
    width: int,
    height: int
) -> list[dict]:
    """Capture screenshots for all URLs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    print(f"Viewport: {width}x{height}", file=sys.stderr)
    print(f"Output: {output_dir}\n", file=sys.stderr)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2  # Retina quality
        )
        page = await context.new_page()

        for url in urls:
            print(f"Capturing: {url}", file=sys.stderr)
            result = await capture_screenshot(page, url, output_dir)
            results.append(result)
            print(file=sys.stderr)

        await browser.close()

    # Summary
    success_count = sum(1 for r in results if r["success"])
    print(f"Captured {success_count}/{len(urls)} screenshots", file=sys.stderr)

    return results


def cli():
    parser = argparse.ArgumentParser(
        description="Capture screenshots matching video clip dimensions"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="URLs to capture"
    )
    parser.add_argument(
        "--video", "-v",
        help="Video file to match dimensions from"
    )
    parser.add_argument(
        "--width", "-W",
        type=int,
        help=f"Viewport width (default: {DEFAULT_WIDTH} or from video)"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        help=f"Viewport height (default: {DEFAULT_HEIGHT} or from video)"
    )
    parser.add_argument(
        "--output", "-o",
        default="media/screenshots/",
        help="Output directory (default: media/screenshots/)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Determine dimensions
    if args.video:
        width, height = get_video_dimensions(args.video)
        print(f"Detected video dimensions: {width}x{height}", file=sys.stderr)
    else:
        width = args.width or DEFAULT_WIDTH
        height = args.height or DEFAULT_HEIGHT

    # Override with explicit dimensions if provided
    if args.width:
        width = args.width
    if args.height:
        height = args.height

    # Run capture
    results = asyncio.run(main(
        urls=args.urls,
        output_dir=Path(args.output),
        width=width,
        height=height
    ))

    if args.json:
        print(json.dumps(results, indent=2))

    success_count = sum(1 for r in results if r["success"])
    sys.exit(0 if success_count == len(args.urls) else 1)


if __name__ == "__main__":
    cli()
