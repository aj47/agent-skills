#!/usr/bin/env python3
"""
Generate YouTube metadata (title, description, tags) from stream transcripts.

Creates SEO-optimized titles, timestamped descriptions with links,
and relevant tags/keywords for YouTube uploads.

Usage:
    python generate_youtube_metadata.py <transcript_path> [--title TITLE] [--output file.md]

Examples:
    python generate_youtube_metadata.py transcript.json
    python generate_youtube_metadata.py parsed.json --title "Testing AI Agents"
    python generate_youtube_metadata.py transcript.txt --output youtube_metadata.md
"""

import re
import sys
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from collections import Counter


# Tool/topic detection for links and tags
TOOLS_WITH_LINKS = {
    'cursor': 'https://cursor.com',
    'claude': 'https://claude.ai',
    'claude code': 'https://claude.ai/claude-code',
    'chatgpt': 'https://chat.openai.com',
    'copilot': 'https://github.com/features/copilot',
    'windsurf': 'https://codeium.com/windsurf',
    'augment': 'https://augmentcode.com',
    'ollama': 'https://ollama.ai',
    'groq': 'https://groq.com',
    'openrouter': 'https://openrouter.ai',
    'playwright': 'https://playwright.dev',
    'playwright mcp': 'https://github.com/microsoft/playwright-mcp',
    'playwriter': 'https://github.com/remorses/playwriter',
    'n8n': 'https://n8n.io',
    'langchain': 'https://langchain.com',
    'llamaindex': 'https://llamaindex.ai',
    'vercel': 'https://vercel.com',
    'anthropic': 'https://anthropic.com',
    'openai': 'https://openai.com',
    'mistral': 'https://mistral.ai',
    'gemini': 'https://gemini.google.com',
}

# SEO keyword categories
SEO_CATEGORIES = {
    'ai_coding': ['ai coding', 'ai programming', 'code assistant', 'ai developer tools', 'vibe coding'],
    'llm': ['llm', 'large language model', 'gpt', 'claude', 'ai model'],
    'automation': ['automation', 'workflow', 'productivity', 'ai agents', 'mcp'],
    'tutorial': ['tutorial', 'how to', 'guide', 'walkthrough', 'demo'],
    'live': ['live stream', 'live coding', 'coding stream', 'tech stream'],
}

# Title hook patterns
TITLE_PATTERNS = [
    "{tool} just {action} in {time}",
    "Testing {tool} Live - {result}",
    "{tool} vs {tool2}: Which is faster?",
    "I tried {tool} for {duration} - Here's what happened",
    "{result} with {tool} | Live Demo",
    "NEW: {tool} can now {capability}",
    "{metric} improvement with {tool}",
]


@dataclass
class TranscriptEntry:
    timestamp: str
    seconds: float
    text: str


@dataclass
class KeyMoment:
    timestamp: str
    seconds: float
    title: str
    description: str
    score: float


@dataclass
class YouTubeMetadata:
    title: str
    description: str
    tags: list[str]
    timestamps: list[tuple[str, str]]  # (timestamp, description)
    tools_mentioned: list[str]
    links: dict[str, str]


def timestamp_to_seconds(ts: str) -> float:
    """Convert HH:MM:SS or MM:SS to seconds."""
    parts = ts.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(ts)


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format (always with hours)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def load_transcript(path: str) -> list[TranscriptEntry]:
    """Load transcript from .txt or .json file."""
    path = Path(path)
    entries = []

    if path.suffix == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'entries' in data:
                for entry in data['entries']:
                    entries.append(TranscriptEntry(
                        timestamp=entry.get('timestamp', '00:00:00'),
                        seconds=entry.get('seconds', 0.0),
                        text=entry.get('text', '')
                    ))
            elif 'sentences' in data:
                for sent in data['sentences']:
                    ts = sent.get('start', 0)
                    entries.append(TranscriptEntry(
                        timestamp=seconds_to_timestamp(ts),
                        seconds=ts,
                        text=sent.get('text', '')
                    ))
    else:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'\[(\d{1,2}:\d{2}:\d{2})\]\s*(.*)', line.strip())
                if match:
                    ts, text = match.groups()
                    entries.append(TranscriptEntry(
                        timestamp=ts,
                        seconds=timestamp_to_seconds(ts),
                        text=text
                    ))

    return entries


def detect_tools(entries: list[TranscriptEntry]) -> list[tuple[str, int]]:
    """Detect tools mentioned and their frequency."""
    full_text = ' '.join(e.text.lower() for e in entries)

    tool_counts = Counter()
    for tool in TOOLS_WITH_LINKS.keys():
        count = full_text.count(tool.lower())
        if count > 0:
            tool_counts[tool] = count

    return tool_counts.most_common(10)


def generate_chapter_title(entries: list[TranscriptEntry], center_idx: int) -> str:
    """Generate a meaningful chapter title from context around a timestamp."""
    # Get context window (5 entries before and after)
    start_idx = max(0, center_idx - 5)
    end_idx = min(len(entries), center_idx + 6)
    context_entries = entries[start_idx:end_idx]
    context_text = ' '.join(e.text.lower() for e in context_entries)

    # Detect tools mentioned in context
    tools_found = []
    for tool in TOOLS_WITH_LINKS.keys():
        if tool in context_text:
            tools_found.append(tool.title())

    # Topic keywords to add specificity
    topic_patterns = [
        (r'(\d+)\s*seconds?', lambda m: f"{m.group(1)} second"),
        (r'browser|web\s*page|screenshot', 'browser automation'),
        (r'speed|fast|slow|time|seconds', 'speed'),
        (r'benchmark', 'benchmark'),
        (r'wordle', 'Wordle challenge'),
        (r'mcp|model context|server', 'MCP'),
        (r'\$\d+', 'pricing'),
        (r'api|endpoint', 'API'),
        (r'local|offline', 'local setup'),
        (r'agent|autonomous', 'agent'),
    ]

    detected_topic = None
    for pattern, topic in topic_patterns:
        match = re.search(pattern, context_text)
        if match:
            if callable(topic):
                detected_topic = topic(match)
            else:
                detected_topic = topic
            break

    # Action patterns to detect what's happening
    action_patterns = [
        (r'setting up|configuring|installing|install', 'Setting up'),
        (r'testing|trying out|let\'s try|let\'s test|running', 'Testing'),
        (r'comparing|versus| vs |compared to', 'Comparing'),
        (r'benchmark|speed test|how fast', 'Benchmark'),
        (r'new record|fastest|best time|record', 'New record:'),
        (r'demo|showing|let me show|watch this', 'Demo:'),
        (r'result|worked|success|done|finished', 'Results:'),
        (r'problem|issue|error|bug|fix|doesn\'t work', 'Troubleshooting'),
        (r'explain|how it works|what is|why does', 'Explaining'),
        (r'discover|found|check this out|look at this', 'Discovery:'),
        (r'\$\d+|price|cost|plan|subscription', 'Pricing'),
        (r'question|q&a|chat asks|someone asked', 'Q&A:'),
    ]

    detected_action = None
    for pattern, action_name in action_patterns:
        if re.search(pattern, context_text):
            detected_action = action_name
            break

    # Build the title with more specificity
    if tools_found and detected_action:
        primary_tool = tools_found[0]
        if detected_topic and detected_topic not in ['speed', 'benchmark']:
            # "New record: Claude 43 second Wordle"
            return f"{detected_action} {primary_tool} {detected_topic}"
        else:
            # "Testing Claude Code"
            return f"{detected_action} {primary_tool}"
    elif tools_found and detected_topic:
        # "Claude Code speed test"
        primary_tool = tools_found[0]
        return f"{primary_tool} {detected_topic}"
    elif tools_found:
        # More specific than just "discussion"
        primary_tool = tools_found[0]
        # Try to find what aspect we're discussing
        if 'how' in context_text or 'why' in context_text:
            return f"How {primary_tool} works"
        elif 'setup' in context_text or 'config' in context_text:
            return f"{primary_tool} configuration"
        elif 'feature' in context_text or 'new' in context_text:
            return f"{primary_tool} features"
        else:
            return f"Using {primary_tool}"
    elif detected_action and detected_topic:
        return f"{detected_action} {detected_topic}"
    elif detected_action:
        return detected_action
    else:
        # No good title could be generated - return None to skip this moment
        return None


def find_key_moments(entries: list[TranscriptEntry]) -> list[KeyMoment]:
    """Find key moments for timestamps section."""
    moments = []

    # High-energy markers (reactions that indicate something interesting)
    energy_markers = [
        'wow', 'whoa', 'incredible', 'amazing', 'insane', 'crazy',
        'new record', 'that worked', 'perfect', 'boom', 'sick'
    ]

    # Topic markers (indicate a new section or topic)
    topic_markers = [
        'let me show', 'testing', 'trying', 'setting up', 'configuring',
        'the answer', 'result', 'benchmark', 'comparing', 'now we',
        'next up', 'moving on', 'let\'s try', 'let\'s see', 'alright so'
    ]

    # Scan for moments
    for i, entry in enumerate(entries):
        text_lower = entry.text.lower()
        score = 0
        reasons = []

        # Check energy markers
        for marker in energy_markers:
            if marker in text_lower:
                score += 3
                reasons.append(marker)

        # Check topic markers
        for marker in topic_markers:
            if marker in text_lower:
                score += 2
                reasons.append(marker)

        # Check for tool mentions (strong signal for chapter)
        for tool in TOOLS_WITH_LINKS.keys():
            if tool in text_lower:
                score += 2

        if score >= 3:
            # Generate a meaningful chapter title from context
            title = generate_chapter_title(entries, i)

            # Skip moments that don't produce good titles
            if title is None:
                continue

            # Get context for description
            context_start = max(0, i - 1)
            context_end = min(len(entries), i + 2)
            context = ' '.join(e.text for e in entries[context_start:context_end])

            # Ensure timestamp is in HH:MM:SS format
            ts = entry.timestamp
            if ts.count(':') == 1:
                ts = '00:' + ts
            # Pad hours if needed
            parts = ts.split(':')
            if len(parts[0]) == 1:
                ts = '0' + ts

            moments.append(KeyMoment(
                timestamp=ts,
                seconds=entry.seconds,
                title=title,
                description=context[:150],
                score=score
            ))

    # Deduplicate moments within 60 seconds of each other
    filtered = []
    for moment in sorted(moments, key=lambda x: x.score, reverse=True):
        is_duplicate = False
        for existing in filtered:
            if abs(moment.seconds - existing.seconds) < 60:
                is_duplicate = True
                break
        if not is_duplicate:
            filtered.append(moment)

    # Sort by timestamp
    return sorted(filtered, key=lambda x: x.seconds)[:15]


def generate_tags(entries: list[TranscriptEntry], tools: list[tuple[str, int]]) -> list[str]:
    """Generate SEO tags from content."""
    tags = []

    # Add tool-specific tags
    for tool, _ in tools[:5]:
        tags.append(tool)
        tags.append(f"{tool} tutorial")
        tags.append(f"{tool} demo")

    # Add category tags
    full_text = ' '.join(e.text.lower() for e in entries)

    for category, keywords in SEO_CATEGORIES.items():
        for keyword in keywords:
            if keyword in full_text:
                tags.append(keyword)

    # Add common tech tags
    common_tags = [
        'ai', 'artificial intelligence', 'coding', 'programming',
        'developer', 'tech', 'software engineering'
    ]
    tags.extend(common_tags)

    # Deduplicate and limit
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)

    return unique_tags[:30]


def generate_title(entries: list[TranscriptEntry], tools: list[tuple[str, int]], custom_title: Optional[str] = None) -> str:
    """Generate an engaging YouTube title."""
    if custom_title:
        return custom_title

    # Get top tool
    top_tool = tools[0][0].title() if tools else "AI Tools"

    # Look for specific results in transcript
    full_text = ' '.join(e.text.lower() for e in entries)

    # Check for benchmark/test content
    if 'benchmark' in full_text or 'test' in full_text:
        if 'record' in full_text:
            return f"{top_tool} Benchmark: New Record! | Live Testing"
        return f"Testing {top_tool} Live | Benchmark Results"

    # Check for comparison content
    if ' vs ' in full_text or 'versus' in full_text or 'compared' in full_text:
        return f"{top_tool} Comparison | Which AI Tool is Best?"

    # Check for tutorial content
    if 'how to' in full_text or 'tutorial' in full_text or 'setup' in full_text:
        return f"{top_tool} Tutorial | Complete Setup Guide"

    # Default title
    return f"{top_tool} Deep Dive | Live Coding & Demo"


def generate_description(
    entries: list[TranscriptEntry],
    tools: list[tuple[str, int]],
    moments: list[KeyMoment],
    title: str
) -> str:
    """Generate full YouTube description with timestamps and links."""

    # Calculate duration
    duration_seconds = entries[-1].seconds if entries else 0
    duration_str = seconds_to_timestamp(duration_seconds)

    # Build description sections
    sections = []

    # Hook/Summary
    hook = f"""🎯 {title}

In this stream, I test and demo various AI tools and share my findings live.
Watch to see real-time benchmarks, comparisons, and honest reactions.
"""
    sections.append(hook)

    # Timestamps
    if moments:
        timestamps_section = "⏱️ TIMESTAMPS\n"
        timestamps_section += f"00:00:00 Intro\n"
        for moment in moments:
            # Clean up the title - remove newlines, keep full text
            clean_title = moment.title.replace('\n', ' ').strip()
            # Ensure timestamp is in HH:MM:SS format
            ts = moment.timestamp
            if ts.count(':') == 1:
                ts = '00:' + ts
            if len(ts.split(':')[0]) == 1:
                ts = '0' + ts
            timestamps_section += f"{ts} {clean_title}\n"
        sections.append(timestamps_section)

    # Tools & Links
    if tools:
        links_section = "🔗 TOOLS MENTIONED\n"
        for tool, count in tools[:8]:
            if tool in TOOLS_WITH_LINKS:
                links_section += f"• {tool.title()}: {TOOLS_WITH_LINKS[tool]}\n"
        sections.append(links_section)

    # Social links (template)
    social_section = """📱 CONNECT
• Twitter/X: https://x.com/techfren
• GitHub: https://github.com/aj47
• Website: https://techfren.net
• Discord: [discord link]
"""
    sections.append(social_section)

    # Hashtags for description
    hashtags = "#AI #Coding #Programming #AITools #TechStream #LiveCoding"
    sections.append(hashtags)

    return "\n".join(sections)


def generate_metadata(
    transcript_path: str,
    custom_title: Optional[str] = None
) -> YouTubeMetadata:
    """Generate complete YouTube metadata from transcript."""

    entries = load_transcript(transcript_path)
    if not entries:
        raise ValueError(f"Could not load transcript from {transcript_path}")

    tools = detect_tools(entries)
    moments = find_key_moments(entries)
    tags = generate_tags(entries, tools)
    title = generate_title(entries, tools, custom_title)
    description = generate_description(entries, tools, moments, title)

    # Build links dict
    links = {}
    for tool, _ in tools:
        if tool in TOOLS_WITH_LINKS:
            links[tool] = TOOLS_WITH_LINKS[tool]

    # Build timestamps list
    timestamps = [(m.timestamp, m.title) for m in moments]

    return YouTubeMetadata(
        title=title,
        description=description,
        tags=tags,
        timestamps=timestamps,
        tools_mentioned=[t[0] for t in tools],
        links=links
    )


def format_output(metadata: YouTubeMetadata) -> str:
    """Format metadata for output."""
    output = f"""# YouTube Metadata

## Title
```
{metadata.title}
```

## Description
```
{metadata.description}
```

## Tags (copy-paste ready)
```
{', '.join(metadata.tags)}
```

## Tools Detected
{chr(10).join(f'- {tool}' for tool in metadata.tools_mentioned[:10])}

## Links
{chr(10).join(f'- {name}: {url}' for name, url in metadata.links.items())}

## Timestamps (for description)
```
00:00:00 Intro
{chr(10).join(f'{ts if ts.count(":") == 2 else "00:" + ts} {title}' for ts, title in metadata.timestamps)}
```

---
*Generated by stream-transcript-processor*
"""
    return output


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    custom_title = None
    output_path = None

    if "--title" in sys.argv:
        idx = sys.argv.index("--title")
        if idx + 1 < len(sys.argv):
            custom_title = sys.argv[idx + 1]

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    try:
        metadata = generate_metadata(path, custom_title)
        output = format_output(metadata)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"YouTube metadata saved to {output_path}")
        else:
            print(output)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
