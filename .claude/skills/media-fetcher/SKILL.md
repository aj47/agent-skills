---
name: media-fetcher
description: Fetch supplementary media (logos, GIFs, landing pages, diagrams, videos) to accompany video clips. Uses APIs and Playwright MCP for browser automation.
---

# Media Fetcher Skill

Fetches contextual media assets to supplement video clips created by the clipper skill. Retrieves logos, reaction GIFs, landing page screenshots, diagrams, and social media videos based on content mentioned in clips.

## Prerequisites

### Required MCP Server: Playwright

This skill requires the Microsoft Playwright MCP server for browser automation. Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--caps", "vision", "--headless"]
    }
  }
}
```

### Required Tools

- **yt-dlp**: For downloading videos from YouTube, TikTok, Instagram, X
  ```bash
  brew install yt-dlp  # macOS
  pip install yt-dlp   # or via pip
  ```

- **Node.js 18+**: For Mermaid diagram rendering
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

### Optional API Keys (Environment Variables)

Set these for enhanced functionality:

```bash
export GIPHY_API_KEY="your_key"      # Get from developers.giphy.com
export BRANDFETCH_API_KEY="your_key" # Get from brandfetch.com/developers (optional, has free CDN)
```

## Quick Start

When the clipper skill has created `segments.json`, you can fetch media for the clips:

```
User: "Fetch media for my clips"
```

You will automatically:
1. Read `segments.json` to understand clip content
2. Extract entities (products, companies, concepts) from each clip
3. Fetch relevant media for each clip
4. Save to `media/` directory with manifest

## Workflow

### Step 1: Analyze Clip Content

Read `segments.json` from the clipper skill. For each clip, extract:

- **Companies/Products**: Brand names mentioned (for logos, landing pages)
- **Concepts**: Technical terms (for diagrams)
- **Emotions**: Reactions, humor (for GIFs)
- **References**: URLs, videos mentioned (for screenshots, video clips)

### Step 2: Fetch Media by Type

For each clip, determine what media would enhance it:

#### Logos (Companies/Products Mentioned)

Use the Brandfetch CDN (no API key needed):

```bash
python .claude/skills/media-fetcher/scripts/fetch_logos.py "github.com" "vercel.com" --output media/logos/
```

Or use Playwright MCP to:
1. Navigate to the company website
2. Screenshot the logo element
3. Save to `media/logos/`

#### Reaction GIFs (Emotional Moments)

```bash
python .claude/skills/media-fetcher/scripts/fetch_gifs.py "mind blown" "excited" --output media/gifs/
```

Requires `GIPHY_API_KEY` environment variable.

#### Landing Pages (Products/Services Mentioned)

Use the capture_screenshot.py script which **automatically matches video dimensions**:

```bash
# Auto-detect dimensions from a clip video file
python .claude/skills/media-fetcher/scripts/capture_screenshot.py \
    "https://github.com/aj47/SpeakMCP" \
    "https://speakmcp.com" \
    --video clips/001_Example.mp4 \
    --output media/screenshots/

# Or specify dimensions directly
python .claude/skills/media-fetcher/scripts/capture_screenshot.py \
    "https://vercel.com" \
    --width 1080 --height 1920
```

**Dimension Matching:**
- Screenshots match your clip video dimensions exactly (ready for overlay)
- Default: Portrait 1080x1920 (9:16 for TikTok/Reels/Shorts)
- Uses ffprobe to detect video dimensions automatically
- Captures viewport only (not full page) to maintain exact dimensions

**Alternative: Use Playwright MCP directly** for interactive capture:
```
1. browser_navigate("https://vercel.com")
2. [Claude sees the page, decides to dismiss cookie banner]
3. browser_click("[data-testid='cookie-accept']")
4. browser_screenshot() -> save to media/screenshots/vercel.png
```

#### Diagrams (Technical Concepts)

Generate Mermaid diagrams based on clip content:

```bash
python .claude/skills/media-fetcher/scripts/render_diagram.py diagram.mmd --output media/diagrams/
```

**Process:**
1. Analyze the technical content in the clip
2. Generate appropriate Mermaid diagram code
3. Render to PNG using mermaid-cli

#### Videos (YouTube, TikTok, Instagram, X)

When a clip references a video or you find a relevant one:

```bash
python .claude/skills/media-fetcher/scripts/download_video.py "https://youtube.com/watch?v=xxx" --output media/videos/
```

**Discovery workflow using Playwright MCP:**
1. `browser_navigate` to YouTube/TikTok search
2. Enter search query based on clip keywords
3. Claude reviews results and selects most relevant
4. Extract video URL
5. Download using yt-dlp

### Step 3: Create Media Manifest

After fetching, create `media_manifest.json`:

```json
{
  "generated_at": "2025-01-15T10:30:00Z",
  "clips": [
    {
      "clip_index": 0,
      "clip_title": "OAuth Setup Guide",
      "media": [
        {
          "type": "logo",
          "source": "brandfetch",
          "entity": "github.com",
          "path": "media/logos/github.png",
          "relevance": "GitHub mentioned as OAuth provider"
        },
        {
          "type": "screenshot",
          "source": "playwright",
          "url": "https://github.com/settings/developers",
          "path": "media/screenshots/github_oauth_settings.png",
          "relevance": "OAuth app registration page shown"
        },
        {
          "type": "diagram",
          "source": "mermaid",
          "description": "OAuth flow diagram",
          "path": "media/diagrams/oauth_flow.png",
          "relevance": "Visualizes the authentication flow discussed"
        }
      ]
    }
  ],
  "summary": {
    "total_clips": 15,
    "logos_fetched": 8,
    "screenshots_captured": 12,
    "gifs_downloaded": 5,
    "diagrams_generated": 3,
    "videos_downloaded": 2
  }
}
```

## Media Types Reference

See [MEDIA_TYPES.md](MEDIA_TYPES.md) for detailed guidance on:
- When to use each media type
- Quality considerations
- Best practices for each source

## Scripts Reference

### fetch_logos.py

Fetches company logos using Brandfetch CDN.

```bash
python .claude/skills/media-fetcher/scripts/fetch_logos.py <domain1> [domain2...] [--output DIR]
```

**Arguments:**
- `domains`: One or more company domains (e.g., "github.com", "stripe.com")
- `--output`: Output directory (default: "media/logos/")

**Output:** PNG files named by domain

### fetch_gifs.py

Searches and downloads GIFs from GIPHY.

```bash
python .claude/skills/media-fetcher/scripts/fetch_gifs.py <query1> [query2...] [--output DIR] [--limit N]
```

**Arguments:**
- `queries`: Search terms (e.g., "mind blown", "celebration")
- `--output`: Output directory (default: "media/gifs/")
- `--limit`: Max GIFs per query (default: 3)

**Requires:** `GIPHY_API_KEY` environment variable

### download_video.py

Downloads videos using yt-dlp.

```bash
python .claude/skills/media-fetcher/scripts/download_video.py <url1> [url2...] [--output DIR] [--max-duration SECONDS]
```

**Arguments:**
- `urls`: Video URLs (YouTube, TikTok, Instagram, X, etc.)
- `--output`: Output directory (default: "media/videos/")
- `--max-duration`: Skip videos longer than N seconds (default: 300)

**Requires:** `yt-dlp` installed

### render_diagram.py

Renders Mermaid diagrams to PNG.

```bash
python .claude/skills/media-fetcher/scripts/render_diagram.py <input.mmd> [--output DIR]
```

**Arguments:**
- `input`: Mermaid diagram file (.mmd)
- `--output`: Output directory (default: "media/diagrams/")

**Requires:** `@mermaid-js/mermaid-cli` (mmdc) installed

### capture_screenshot.py

Captures screenshots with dimensions matching your video clips.

```bash
python .claude/skills/media-fetcher/scripts/capture_screenshot.py <url1> [url2...] [options]
```

**Arguments:**
- `urls`: One or more URLs to capture
- `--video, -v`: Video file to match dimensions from (uses ffprobe)
- `--width, -W`: Viewport width (default: 1080)
- `--height, -H`: Viewport height (default: 1920)
- `--output, -o`: Output directory (default: "media/screenshots/")

**Features:**
- Auto-detects video dimensions via ffprobe
- Default: Portrait 1080x1920 (9:16 ratio for TikTok/Reels/Shorts)
- Auto-dismisses cookie banners and popups
- 2x device scale for retina quality
- Viewport-only capture (matches exact dimensions)

**Requires:** `playwright` Python package, Chromium browser

## Using Playwright MCP for Browser Tasks

For landing pages and video discovery, use the Playwright MCP tools directly:

### Available Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Go to URL |
| `browser_screenshot` | Capture current page |
| `browser_click` | Click element by selector or text |
| `browser_type` | Type text into input field |
| `browser_scroll` | Scroll page up/down |
| `browser_snapshot` | Get accessibility tree (structured data) |

### Example: Capture Landing Page

```
1. browser_navigate("https://stripe.com")
   → Page loads, Claude sees accessibility snapshot

2. [If cookie banner detected]
   browser_click("Accept cookies")
   → Banner dismissed

3. browser_screenshot()
   → Returns base64 image, save to media/screenshots/stripe.png
```

### Example: Find YouTube Video

```
1. browser_navigate("https://youtube.com")

2. browser_type("[name='search_query']", "OAuth tutorial 2024")

3. browser_click("[id='search-icon-legacy']")
   → Search results load

4. [Claude reviews results, picks most relevant]
   browser_snapshot()
   → Get video URLs from accessibility tree

5. Extract URL, pass to download_video.py
```

## Output Structure

```
media/
├── logos/
│   ├── github.png
│   ├── vercel.png
│   └── stripe.png
├── screenshots/
│   ├── github_oauth_settings.png
│   └── stripe_dashboard.png
├── gifs/
│   ├── mind_blown_001.gif
│   └── celebration_001.gif
├── diagrams/
│   ├── oauth_flow.png
│   └── api_architecture.png
├── videos/
│   ├── youtube_abc123.mp4
│   └── tiktok_xyz789.mp4
└── media_manifest.json
```

## Integration with Clipper Skill

This skill is designed to work alongside the clipper skill:

1. **Clipper** analyzes transcription → creates `segments.json`
2. **Media-fetcher** reads `segments.json` → fetches contextual media
3. Output: Clips in `clips/` + media in `media/` + `media_manifest.json`

The manifest links each media asset to its corresponding clip for easy integration.

## Troubleshooting

**"Playwright MCP not found"**: Ensure the MCP server is configured in your Claude Code settings. Run `npx @playwright/mcp@latest` to verify it's installed.

**"yt-dlp: command not found"**: Install with `brew install yt-dlp` or `pip install yt-dlp`.

**"GIPHY_API_KEY not set"**: Get a free API key from developers.giphy.com and set the environment variable.

**"mmdc: command not found"**: Install Mermaid CLI with `npm install -g @mermaid-js/mermaid-cli`.

**Rate limits**: GIPHY has 100 requests/hour on beta keys. Brandfetch CDN has no limits. YouTube search via Playwright has no API limits.
