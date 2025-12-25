#!/usr/bin/env python3
"""
Capture screenshots for clip 002: Building Multi-Agent Orchestration with ACP Protocol

URLs to capture:
- SpeakMCP GitHub: https://github.com/aj47/SpeakMCP
- SpeakMCP Landing: https://speakmcp.com/
- ACP Protocol GitHub: https://github.com/i-am-bee/acp
- ACP Protocol Docs: https://agentcommunicationprotocol.dev/
- Augment Code: https://augmentcode.com/
"""

import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright


URLS = [
    {
        "name": "speakmcp_github",
        "url": "https://github.com/aj47/SpeakMCP",
        "description": "SpeakMCP GitHub repository"
    },
    {
        "name": "speakmcp_landing",
        "url": "https://speakmcp.com/",
        "description": "SpeakMCP landing page"
    },
    {
        "name": "acp_github",
        "url": "https://github.com/i-am-bee/acp",
        "description": "ACP Protocol GitHub (IBM)"
    },
    {
        "name": "acp_docs",
        "url": "https://agentcommunicationprotocol.dev/",
        "description": "ACP Protocol documentation"
    },
    {
        "name": "augment_code",
        "url": "https://augmentcode.com/",
        "description": "Augment Code (Augi) landing page"
    }
]


async def capture_screenshot(page, url_info: dict, output_dir: Path) -> dict:
    """Capture a screenshot of a URL."""
    result = {
        "name": url_info["name"],
        "url": url_info["url"],
        "description": url_info["description"],
        "success": False,
        "path": None,
        "error": None
    }

    output_path = output_dir / f"{url_info['name']}.png"

    try:
        print(f"  Navigating to {url_info['url']}...")
        await page.goto(url_info["url"], wait_until="networkidle", timeout=30000)

        # Try to dismiss common overlays/cookie banners
        for selector in [
            "text=Accept",
            "text=Accept all",
            "text=I agree",
            "text=Got it",
            "[aria-label='Close']",
            ".cookie-banner button",
        ]:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    await element.click()
                    await page.wait_for_timeout(500)
            except:
                pass

        # Wait a bit for any animations
        await page.wait_for_timeout(1000)

        # Take screenshot
        await page.screenshot(path=str(output_path), full_page=False)

        result["success"] = True
        result["path"] = str(output_path)
        print(f"  ✓ Saved: {output_path}")

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ Failed: {e}")

    return result


async def main():
    output_dir = Path(__file__).parent / "screenshots"
    output_dir.mkdir(exist_ok=True)

    print("Starting screenshot capture for clip 002...")
    print(f"Output directory: {output_dir}\n")

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=2  # Retina quality
        )
        page = await context.new_page()

        for url_info in URLS:
            print(f"Capturing: {url_info['description']}")
            result = await capture_screenshot(page, url_info, output_dir)
            results.append(result)
            print()

        await browser.close()

    # Summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\nCapture complete: {success_count}/{len(URLS)} screenshots saved")

    return results


if __name__ == "__main__":
    asyncio.run(main())
