#!/usr/bin/env python3
"""
Fetch company logos using Brandfetch CDN or Clearbit.

Usage:
    python fetch_logos.py github.com vercel.com stripe.com --output media/logos/

No API key required for basic usage (uses public CDN endpoints).
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


# Logo sources in priority order
LOGO_SOURCES = [
    # Clearbit (shutting down Dec 2025, but still works)
    "https://logo.clearbit.com/{domain}",
    # Brandfetch CDN
    "https://cdn.brandfetch.io/id/{domain}/w/400/h/400?c=1id",
    # Google favicon as last resort
    "https://www.google.com/s2/favicons?domain={domain}&sz=128",
]


def normalize_domain(domain: str) -> str:
    """Clean up domain input (remove https://, trailing slashes, etc.)"""
    domain = domain.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.replace("www.", "")
    domain = domain.rstrip("/")
    # Remove path if present
    if "/" in domain:
        domain = domain.split("/")[0]
    return domain


def fetch_logo(domain: str, output_dir: Path) -> dict:
    """
    Fetch logo for a domain from available sources.

    Returns dict with status and details.
    """
    domain = normalize_domain(domain)
    result = {
        "domain": domain,
        "success": False,
        "source": None,
        "path": None,
        "error": None
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{domain.replace('.', '_')}.png"

    for source_template in LOGO_SOURCES:
        url = source_template.format(domain=domain)
        try:
            # Create request with user agent (some CDNs block default Python UA)
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "image/png,image/jpeg,image/*"
                }
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    content = response.read()

                    # Check if we got actual image data (not error page)
                    if len(content) > 1000:  # Reasonable minimum for a logo
                        with open(output_path, "wb") as f:
                            f.write(content)

                        result["success"] = True
                        result["source"] = source_template.split("/")[2]  # Extract domain
                        result["path"] = str(output_path)
                        return result

        except urllib.error.HTTPError as e:
            # Try next source
            continue
        except urllib.error.URLError as e:
            # Network error, try next source
            continue
        except Exception as e:
            # Unexpected error, try next source
            continue

    result["error"] = "Logo not found in any source"
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fetch company logos from Brandfetch/Clearbit CDN"
    )
    parser.add_argument(
        "domains",
        nargs="+",
        help="Company domains (e.g., github.com stripe.com)"
    )
    parser.add_argument(
        "--output", "-o",
        default="media/logos/",
        help="Output directory (default: media/logos/)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()
    output_dir = Path(args.output)

    results = []
    success_count = 0

    for domain in args.domains:
        result = fetch_logo(domain, output_dir)
        results.append(result)

        if result["success"]:
            success_count += 1
            print(f"✓ {result['domain']}: {result['path']}", file=sys.stderr)
        else:
            print(f"✗ {result['domain']}: {result['error']}", file=sys.stderr)

    # Summary
    print(f"\nFetched {success_count}/{len(args.domains)} logos", file=sys.stderr)

    if args.json:
        import json
        print(json.dumps(results, indent=2))

    # Exit with error if any failed
    sys.exit(0 if success_count == len(args.domains) else 1)


if __name__ == "__main__":
    main()
