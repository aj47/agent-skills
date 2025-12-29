# Voice Patterns Reference

Detection patterns for identifying clip-worthy and post-worthy moments in techfren stream transcripts.

---

## High-Energy Markers

Words that signal excitement, discovery, or reaction moments worth capturing.

### Exclamations (Score: +3 per occurrence)
```python
HIGH_ENERGY = [
    "dude", "whoa", "wow", "sick", "boom", "perfect", "insane",
    "that's actually", "let's see", "here we go", "check this out",
    "wait", "oh my", "holy", "crazy", "incredible", "amazing"
]
```

### Demo Starters (Score: +2)
```python
DEMO_PHRASES = [
    "let's see", "let's try", "here we go", "let's go",
    "let me show you", "watch this", "check this out"
]
```

### Natural Reactions (Score: +2)
```python
REACTIONS = [
    "cool", "nice", "wow", "dude", "boom", "sick",
    "there we go", "that's it", "done", "perfect"
]
```

---

## Value Proposition Markers

Words that indicate tool/product value - these make content more engaging.

### Value Props (Score: +2 each)
```python
VALUE_PROPS = {
    'free': ["free", "no cost", "zero cost", "costs nothing", "$0"],
    'open_source': ["open source", "opensource", "open-source", "oss", "github"],
    'local': ["local", "locally", "runs locally", "on device", "offline", "private"],
    'no_install': ["no install", "no installation", "browser", "web-based"],
    'no_signup': ["no signup", "no sign up", "no account", "no registration"],
    'fast': ["fast", "quick", "instant", "lightning", "blazing", "2 seconds"],
    'easy': ["easy", "simple", "straightforward", "one click", "drop-in"]
}
```

---

## Discovery Markers

Signals that indicate finding something new or noteworthy.

### Discovery Phrases (Score: +4)
```python
DISCOVERY = [
    "trending", "just discovered", "found something", "new tool",
    "just shipped", "check out", "this changes", "haven't seen",
    "first time", "brand new", "just released", "20k stars", "10k stars",
    "blowing up", "going viral"
]
```

### Metric Indicators (Score: +3)
```python
METRICS = [
    "stars", "downloads", "users", "seconds", "minutes",
    "faster", "smaller", "bigger", "percent", "%"
]
```

---

## Comparison Markers

Words indicating tool comparisons - high engagement content.

### Comparison Phrases (Score: +4)
```python
COMPARISON = [
    "better than", "beats", "faster than", "unlike",
    "instead of", "replaced", "switched from", "compared to",
    "vs", "versus", "alternative to"
]
```

### Superlatives (Score: +3)
```python
SUPERLATIVES = [
    "best", "fastest", "easiest", "first", "only",
    "most", "top", "number one", "#1"
]
```

---

## Problem-Solution Markers

Narrative arcs that make great clips.

### Resolution Phrases (Score: +4)
```python
RESOLUTION = [
    "finally", "figured it out", "the fix was", "turns out",
    "that's why", "now it makes sense", "the solution",
    "the answer", "here's how", "the trick"
]
```

### Breakthrough Moments (Score: +3)
```python
BREAKTHROUGH = [
    "it worked", "it works", "there we go", "boom",
    "got it", "success", "done", "that's it"
]
```

---

## Tool Categories

Known tools to detect and categorize content.

```python
TOOLS = {
    'ai_coding': [
        'cursor', 'copilot', 'windsurf', 'augment', 'aide',
        'cody', 'continue', 'tabnine', 'codeium'
    ],
    'llms': [
        'claude', 'gpt', 'chatgpt', 'ollama', 'llama', 'mistral',
        'gemini', 'groq', 'openai', 'anthropic', 'perplexity'
    ],
    'frameworks': [
        'autogen', 'langchain', 'llamaindex', 'crewai',
        'n8n', 'flowise', 'dify', 'semantic kernel'
    ],
    'local': [
        'ollama', 'lmstudio', 'localai', 'jan', 'gpt4all',
        'mlx', 'llama.cpp', 'koboldcpp'
    ]
}
```

---

## Scoring Priority

How to rank detected moments (highest to lowest):

| Priority | Signal | Score | Example |
|----------|--------|-------|---------|
| 1 | Tool name + specific result | 5 | "Cursor completed the function in 2 seconds" |
| 2 | Comparison to known tool | 4 | "This beats ChatGPT for coding" |
| 3 | Metric or number | 3 | "Went from 500ms to 50ms" |
| 4 | Strong reaction word | 2 | "Whoa, that's incredible" |
| 5 | General discovery energy | 1 | "This is pretty cool" |

**Thresholds:**
- Score 5+: **High priority** - Definitely clip/post
- Score 3-4: **Medium priority** - Worth considering
- Score 1-2: **Low priority** - Skip unless needed

---

## Anti-Patterns

### Slow Starts to SKIP (5x more common in failures)
- Sentences starting with "so"
- "hey friends", "what's up"
- "alright so", "okay so"
- "I wanted to show you"

### Hedging Words to SKIP
- "I think", "kind of", "maybe"
- "basically", "like" (as filler)
- "honestly", "literally"

### Skip Entirely
- Off-topic tangents
- Incomplete thoughts
- Negative content without resolution
- Generic excitement without specifics

---

## Detection Algorithm

```python
def score_moment(text: str) -> tuple[int, list[str]]:
    """Score a transcript moment for clip/post potential."""
    score = 0
    reasons = []
    text_lower = text.lower()

    # Check high-energy markers
    for marker in HIGH_ENERGY:
        if marker in text_lower:
            score += 3
            reasons.append(f"energy: '{marker}'")

    # Check value props
    for prop_name, patterns in VALUE_PROPS.items():
        for pattern in patterns:
            if pattern in text_lower:
                score += 2
                reasons.append(f"value: '{prop_name}'")
                break

    # Check discovery markers
    for marker in DISCOVERY:
        if marker in text_lower:
            score += 4
            reasons.append(f"discovery: '{marker}'")

    # Check tool mentions
    for category, tools in TOOLS.items():
        for tool in tools:
            if tool in text_lower:
                score += 1
                reasons.append(f"tool: '{tool}'")
                break

    # Check for results
    for marker in BREAKTHROUGH:
        if marker in text_lower:
            score += 3
            reasons.append(f"result: '{marker}'")

    return score, reasons
```

---

## Integration Note

This file provides detection patterns. For writing guidelines (what words to use when drafting posts), see:
- [x-post-extractor/VOICE.md](../../x-post-extractor/VOICE.md)
- [x-post-extractor/FORMATS.md](../../x-post-extractor/FORMATS.md)
