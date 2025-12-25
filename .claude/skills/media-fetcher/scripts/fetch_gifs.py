#!/usr/bin/env python3
"""
Fetch reaction GIFs from GIPHY API.

Usage:
    python fetch_gifs.py "mind blown" "excited" --output media/gifs/ --limit 3

Requires GIPHY_API_KEY environment variable.
Get a free API key at: https://developers.giphy.com/
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


GIPHY_SEARCH_URL = "https://api.giphy.com/v1/gifs/search"


def get_api_key() -> str:
    """Get GIPHY API key from environment."""
    key = os.environ.get("GIPHY_API_KEY")
    if not key:
        print("Error: GIPHY_API_KEY environment variable not set", file=sys.stderr)
        print("Get a free API key at: https://developers.giphy.com/", file=sys.stderr)
        sys.exit(1)
    return key


def search_gifs(query: str, api_key: str, limit: int = 3) -> list:
    """
    Search GIPHY for GIFs matching query.

    Returns list of GIF data dicts.
    """
    params = urllib.parse.urlencode({
        "api_key": api_key,
        "q": query,
        "limit": limit,
        "rating": "pg-13",  # Keep it appropriate
        "lang": "en"
    })

    url = f"{GIPHY_SEARCH_URL}?{params}"

    try:
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])

    except urllib.error.HTTPError as e:
        print(f"GIPHY API error: {e.code}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error searching GIPHY: {e}", file=sys.stderr)
        return []


def download_gif(gif_data: dict, output_dir: Path, query: str, index: int) -> dict:
    """
    Download a GIF from GIPHY data.

    Prefers MP4 format for smaller file size.
    """
    result = {
        "query": query,
        "title": gif_data.get("title", ""),
        "success": False,
        "path": None,
        "format": None,
        "error": None
    }

    images = gif_data.get("images", {})

    # Prefer MP4 (smaller file size), fallback to GIF
    formats_to_try = [
        ("original", "mp4", "mp4"),  # (key, url_suffix, extension)
        ("fixed_height", "mp4", "mp4"),
        ("original", "url", "gif"),
        ("fixed_height", "url", "gif"),
    ]

    download_url = None
    extension = None

    for format_key, url_key, ext in formats_to_try:
        format_data = images.get(format_key, {})
        url = format_data.get(url_key)
        if url:
            download_url = url
            extension = ext
            break

    if not download_url:
        result["error"] = "No downloadable format found"
        return result

    # Clean query for filename
    safe_query = "".join(c if c.isalnum() else "_" for c in query)
    filename = f"{safe_query}_{index:03d}.{extension}"
    output_path = output_dir / filename

    try:
        request = urllib.request.Request(
            download_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()

            with open(output_path, "wb") as f:
                f.write(content)

            result["success"] = True
            result["path"] = str(output_path)
            result["format"] = extension
            result["size_kb"] = len(content) // 1024

    except Exception as e:
        result["error"] = str(e)

    return result


def fetch_gifs_for_query(query: str, api_key: str, output_dir: Path, limit: int) -> list:
    """Fetch and download GIFs for a single query."""
    results = []

    gifs = search_gifs(query, api_key, limit)

    if not gifs:
        results.append({
            "query": query,
            "success": False,
            "error": "No GIFs found"
        })
        return results

    for i, gif_data in enumerate(gifs):
        result = download_gif(gif_data, output_dir, query, i + 1)
        results.append(result)

        if result["success"]:
            print(f"✓ {query}[{i+1}]: {result['path']} ({result['size_kb']}KB)", file=sys.stderr)
        else:
            print(f"✗ {query}[{i+1}]: {result['error']}", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch reaction GIFs from GIPHY"
    )
    parser.add_argument(
        "queries",
        nargs="+",
        help="Search queries (e.g., 'mind blown' 'excited')"
    )
    parser.add_argument(
        "--output", "-o",
        default="media/gifs/",
        help="Output directory (default: media/gifs/)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=3,
        help="Max GIFs per query (default: 3)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    api_key = get_api_key()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    success_count = 0
    total_count = 0

    for query in args.queries:
        results = fetch_gifs_for_query(query, api_key, output_dir, args.limit)
        all_results.extend(results)

        for r in results:
            total_count += 1
            if r.get("success"):
                success_count += 1

    # Summary
    print(f"\nDownloaded {success_count}/{total_count} GIFs", file=sys.stderr)

    if args.json:
        print(json.dumps(all_results, indent=2))

    sys.exit(0 if success_count > 0 else 1)


if __name__ == "__main__":
    main()
