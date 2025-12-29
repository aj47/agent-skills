#!/usr/bin/env python3
"""
Generate script notes from a transcript segment for short-form content recording.

This script transforms transcript segments into sentence starters following
the techfren voice guide format: HOOK, VALUE STACK, DEMO, CLOSE.

Usage:
    python generate_script_notes.py <transcript_path> <start_ts> <end_ts> [--output file.md]

Examples:
    python generate_script_notes.py transcript.txt 01:23:00 01:24:30
    python generate_script_notes.py parsed.json 01:23:00 01:25:00 --output notes.md
"""

import re
import sys
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# Tool categories for detection
TOOLS = {
    'ai_coding': ['cursor', 'copilot', 'windsurf', 'augment', 'aide', 'cody', 'continue'],
    'llms': ['claude', 'gpt', 'chatgpt', 'ollama', 'llama', 'mistral', 'gemini', 'groq', 'openai', 'anthropic'],
    'frameworks': ['autogen', 'langchain', 'llamaindex', 'crewai', 'n8n', 'flowise', 'dify'],
    'local': ['ollama', 'lmstudio', 'localai', 'jan', 'gpt4all', 'mlx']
}

# Value proposition patterns
VALUE_PROPS = {
    'free': ['free', 'no cost', 'zero cost', 'costs nothing'],
    'open_source': ['open source', 'opensource', 'open-source', 'oss'],
    'local': ['local', 'locally', 'runs locally', 'on device', 'on-device', 'offline'],
    'no_install': ['no install', 'no installation', 'browser', 'web-based'],
    'no_signup': ['no signup', 'no sign up', 'no account', 'no registration'],
    'fast': ['fast', 'quick', 'instant', 'lightning', 'blazing'],
    'easy': ['easy', 'simple', 'straightforward', 'one click', '1-click']
}


@dataclass
class TranscriptEntry:
    timestamp: str
    seconds: float
    text: str


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


def load_transcript(path: str) -> list[TranscriptEntry]:
    """Load transcript from .txt or .json file."""
    path = Path(path)
    entries = []

    if path.suffix == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle different JSON formats
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
                    h, m, s = int(ts // 3600), int((ts % 3600) // 60), int(ts % 60)
                    entries.append(TranscriptEntry(
                        timestamp=f"{h:02d}:{m:02d}:{s:02d}",
                        seconds=ts,
                        text=sent.get('text', '')
                    ))
    else:
        # Plain text format: [HH:MM:SS] text
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*(.*)', line.strip())
                if match:
                    ts, text = match.groups()
                    entries.append(TranscriptEntry(
                        timestamp=ts,
                        seconds=timestamp_to_seconds(ts),
                        text=text
                    ))

    return entries


def extract_segment(entries: list[TranscriptEntry], start: str, end: str) -> str:
    """Extract transcript text between timestamps."""
    start_sec = timestamp_to_seconds(start)
    end_sec = timestamp_to_seconds(end)

    segment_texts = []
    for entry in entries:
        if start_sec <= entry.seconds <= end_sec:
            segment_texts.append(entry.text)

    return ' '.join(segment_texts)


def detect_tool(text: str) -> Optional[str]:
    """Detect mentioned tool from text."""
    text_lower = text.lower()

    for category, tools in TOOLS.items():
        for tool in tools:
            if tool in text_lower:
                return tool.title()

    return None


def detect_value_props(text: str) -> list[str]:
    """Detect value propositions in text."""
    text_lower = text.lower()
    found = []

    for prop_name, patterns in VALUE_PROPS.items():
        for pattern in patterns:
            if pattern in text_lower:
                found.append(prop_name)
                break

    return found


def extract_claim(text: str) -> Optional[str]:
    """Extract a bold claim or result statement."""
    sentences = re.split(r'[.!?]', text)

    claim_indicators = [
        'trending', 'stars', 'downloads', 'best', 'fastest', 'easiest',
        'first', 'never seen', 'game changer', 'incredible', 'insane',
        'amazing', 'blew my mind', 'mind-blowing'
    ]

    for sent in sentences:
        sent_lower = sent.lower()
        for indicator in claim_indicators:
            if indicator in sent_lower:
                claim = sent.strip()
                if len(claim) > 10 and len(claim) < 150:
                    return claim

    # Fallback: first sentence with numbers
    for sent in sentences:
        if re.search(r'\d+', sent):
            claim = sent.strip()
            if len(claim) > 10 and len(claim) < 150:
                return claim

    return None


def generate_script_notes(
    segment: str,
    tool: Optional[str] = None,
    start_ts: str = "00:00:00",
    end_ts: str = "00:00:00"
) -> str:
    """Generate script notes from transcript segment."""

    # Auto-detect elements if not provided
    if not tool:
        tool = detect_tool(segment) or "[Tool Name]"

    value_props = detect_value_props(segment)
    claim = extract_claim(segment) or "[Bold claim or result]"

    # Build value prop bullet points
    value_bullets = []
    if 'free' in value_props:
        value_bullets.append("It's completely free...")
    if 'open_source' in value_props:
        value_bullets.append("Open source, so you can see exactly what's running...")
    if 'local' in value_props:
        value_bullets.append("Runs completely locally, no data leaves your machine...")
    if 'no_install' in value_props:
        value_bullets.append("No installation required...")
    if 'no_signup' in value_props:
        value_bullets.append("No signup, just start using it...")
    if 'fast' in value_props:
        value_bullets.append("Super fast...")
    if 'easy' in value_props:
        value_bullets.append("Dead simple to use...")

    # Default value bullets if none detected
    if not value_bullets:
        value_bullets = [
            f"I use {tool} and...",
            "No [pain point]...",
            "[Key benefit]..."
        ]

    # Truncate segment preview
    preview = segment[:400] + "..." if len(segment) > 400 else segment

    notes = f"""# Script Notes: {tool}

**Source:** [{start_ts} - {end_ts}]

---

## HOOK
*First 3 seconds - stop the scroll*

- {claim}...
- This is {tool} and it...

---

## VALUE STACK
*Stack benefits quickly, use "just" liberally*

"""
    for bullet in value_bullets[:3]:
        notes += f"- {bullet}\n"

    notes += f"""
---

## DEMO
*Show, don't tell. React naturally.*

- Let's try it out...
- [First action]...
- Let's see if this works...
- [React: dude, whoa, sick, boom, there we go]

---

## CLOSE
*Quick recap + action CTA*

- [One-line recap]...
- Go download it / Check it out / Give it a try...

---

## Power Words

Use these naturally throughout:
- **Simplicity:** just, that's it, done
- **Energy:** dude, whoa, boom, sick, pretty cool
- **Inclusivity:** let's see, let's try, here we go
- **Results:** there we go, it works, boom

---

## DON'T Start With

- "So..." (kills retention)
- "Hey what's up..." (slow start)
- "I wanted to show you..." (boring)
- "In this video..." (skip-inducing)

---

## Source Segment

> {preview}

---

*Generated from stream transcript*
"""

    return notes


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        print("\nUsage: python generate_script_notes.py <transcript_path> <start_ts> <end_ts> [--output file.md]")
        sys.exit(1)

    path = sys.argv[1]
    start_ts = sys.argv[2]
    end_ts = sys.argv[3]

    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # Load and extract segment
    entries = load_transcript(path)
    if not entries:
        print(f"ERROR: Could not load transcript from {path}")
        sys.exit(1)

    segment = extract_segment(entries, start_ts, end_ts)
    if not segment:
        print(f"ERROR: No content found between {start_ts} and {end_ts}")
        sys.exit(1)

    # Generate script notes
    notes = generate_script_notes(segment, start_ts=start_ts, end_ts=end_ts)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes)
        print(f"Script notes saved to {output_path}")
    else:
        print(notes)


if __name__ == "__main__":
    main()
