#!/usr/bin/env python3
"""
Draft X posts from transcript segments.

Quick X post drafting based on transcript content with different styles:
discovery, result, comparison, or tutorial.

Usage:
    python draft_x_posts.py <transcript_path> <timestamp> [--style STYLE] [--output file.md]

Styles:
    discovery  - "Just discovered X..." format
    result     - "Just built/shipped X..." format
    comparison - "X vs Y" or "Better than..." format
    tutorial   - Thread format with steps

Examples:
    python draft_x_posts.py transcript.txt 01:23:45
    python draft_x_posts.py parsed.json 01:23:45 --style discovery
    python draft_x_posts.py transcript.txt 01:23:45 --output post.md
"""

import re
import sys
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# Tool names for detection
TOOLS = [
    'cursor', 'claude', 'gpt', 'chatgpt', 'copilot', 'windsurf', 'augment',
    'ollama', 'llama', 'mistral', 'groq', 'gemini', 'openai', 'anthropic',
    'autogen', 'langchain', 'n8n', 'flowise', 'aide', 'cody', 'continue',
    'dify', 'crewai', 'llamaindex', 'jan', 'lmstudio', 'gpt4all'
]

# Hook templates by style
HOOK_TEMPLATES = {
    'discovery': [
        "{tool} has been trending. {metric}. {what_it_does}",
        "Just discovered {tool}. {surprise}",
        "Now this is something I haven't seen in any other {category}",
        "{tool} is {adjective}. Here's what I found"
    ],
    'result': [
        "Just {action} {result} with {tool}",
        "{number} {unit} with {tool}. Here's what happened",
        "Built {result} in {time}. No {pain_point} required"
    ],
    'comparison': [
        "{tool} is the best {category} I've tried. Here's why",
        "Forget {old_tool}. {new_tool} just {advantage}",
        "A year ago this was impossible. Just did it in {time}"
    ],
    'tutorial': [
        "How to {action} with {tool}:",
        "{result} in {steps} steps:",
        "The {tool} workflow that changed how I {action}:"
    ]
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


def extract_context(entries: list[TranscriptEntry], timestamp: str, window_minutes: int = 3) -> str:
    """Extract context around a timestamp."""
    target_sec = timestamp_to_seconds(timestamp)
    window_sec = window_minutes * 60

    context_texts = []
    for entry in entries:
        if abs(entry.seconds - target_sec) <= window_sec:
            context_texts.append(entry.text)

    return ' '.join(context_texts)


def detect_tool(text: str) -> Optional[str]:
    """Detect mentioned tool from text."""
    text_lower = text.lower()
    for tool in TOOLS:
        if tool in text_lower:
            return tool.title()
    return None


def detect_style(text: str) -> str:
    """Auto-detect best post style from content."""
    text_lower = text.lower()

    # Discovery signals
    discovery_signals = ['trending', 'discovered', 'found', 'new', 'just released', 'shipped']
    if any(signal in text_lower for signal in discovery_signals):
        return 'discovery'

    # Comparison signals
    comparison_signals = ['better than', 'vs', 'compared to', 'forget', 'switch', 'instead of']
    if any(signal in text_lower for signal in comparison_signals):
        return 'comparison'

    # Tutorial signals
    tutorial_signals = ['how to', 'step by step', 'steps', 'first', 'then', 'finally']
    if any(signal in text_lower for signal in tutorial_signals):
        return 'tutorial'

    # Default to result
    return 'result'


def generate_x_post(context: str, style: Optional[str] = None, timestamp: str = "00:00:00") -> str:
    """Generate X post draft from context."""

    if not style:
        style = detect_style(context)

    tool = detect_tool(context) or "[Tool]"

    # Base templates by style
    if style == 'discovery':
        post_content = f"""Just discovered {tool}.

The part that surprised me: [what was unexpected]

[Why this matters / the bigger pattern]

Give it a try: [link]"""

    elif style == 'comparison':
        post_content = f"""Been using {tool} for [time period].

It's genuinely better than [alternative] at [specific thing].

The gap that keeps hitting me: a year ago this didn't exist.

[link or action CTA]"""

    elif style == 'tutorial':
        post_content = f"""How to [action] with {tool}:

1. [First step]
2. [Second step]
3. [Third step]

[Result or benefit]

Full breakdown: [link]"""

    else:  # result
        post_content = f"""Just [action] with {tool}.

[Specific result or metric]

No [pain point]. Just [benefit].

[link or how to try it]"""

    # Preview of source context
    preview = context[:250] + "..." if len(context) > 250 else context

    output = f"""# X Post Draft

**Style:** {style.upper()}
**Source timestamp:** {timestamp}
**Detected tool:** {tool}

---

## Copy-Paste Ready:

```
{post_content}
```

---

## Formatting Reminders

- First line = hook (stop the scroll)
- Whitespace between thoughts
- No text walls
- End with action CTA
- Keep each thought under 280 chars

## Hook Checklist

- [ ] First word is NOT: so, hey, I, just wanted, what's up
- [ ] First 10 words are a hook, not context
- [ ] Tool/topic named in first line
- [ ] Bold claim or surprising result upfront

---

## Source Context

> {preview}

---

*Draft generated from stream transcript at {timestamp}*
"""

    return output


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    timestamp = sys.argv[2]

    style = None
    output_path = None

    if "--style" in sys.argv:
        idx = sys.argv.index("--style")
        if idx + 1 < len(sys.argv):
            style = sys.argv[idx + 1].lower()

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # Load and extract context
    entries = load_transcript(path)
    if not entries:
        print(f"ERROR: Could not load transcript from {path}")
        sys.exit(1)

    context = extract_context(entries, timestamp)
    if not context:
        print(f"ERROR: No content found around {timestamp}")
        sys.exit(1)

    # Generate post
    post = generate_x_post(context, style, timestamp)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(post)
        print(f"X post draft saved to {output_path}")
    else:
        print(post)


if __name__ == "__main__":
    main()
