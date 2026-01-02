# Narrative Templates

Story arc templates for detecting narrative-complete clips. Each template defines required beats that must be present for a clip to tell a complete story.

## Why Narrative Templates?

The problem: Finding isolated "interesting moments" (reactions, tips, opinions) but missing narrative completeness. Example:
- **Found**: Thesis ("Skills can replace MCPs")
- **Found**: Conclusion ("It worked!")
- **MISSED**: The demo proving the thesis (the most valuable content)

Templates ensure we capture complete story arcs, not just peaks.

---

## Template 1: ARGUMENT

**Use case**: Claims, hot takes, thesis statements that need proof

### Required Beats

| Beat | Description | Minimum | Score Boost |
|------|-------------|---------|-------------|
| CLAIM | The thesis/assertion being made | YES | +4 |
| EVIDENCE | Proof supporting the claim (demo, example, data) | YES | +15 |
| RESOLUTION | Outcome confirming/denying claim | YES | +8 |

### Optional Beats

| Beat | Description | Score Boost |
|------|-------------|-------------|
| STAKES | Why this matters | +2 |
| COUNTER | Addressing objections | +2 |

### Detection Signals

**CLAIM patterns:**
- "I think...", "My thesis is...", "The argument is..."
- "Skills can...", "MCPs are...", "The difference is..."
- "Here's the thing...", "Unpopular opinion..."
- Strong assertion language

**EVIDENCE patterns:**
- "Let me show you...", "Watch this...", "Here's proof..."
- "So if I...", "Let me prove it...", "Let me demonstrate..."
- Tool invocations, code execution, live demos
- "Check this out...", "Look at this..."

**RESOLUTION patterns:**
- "See?", "There you go", "It worked!"
- "That proves...", "And that's why..."
- "Boom", "Done", victory reactions
- Return to original claim with confirmation

### Example Match

```
[CLAIM] "My thesis is that skills can completely replace MCPs..."
   ↓ (10-30 seconds)
[STAKES] "Everyone's building MCPs but they're overkill for most use cases"
   ↓ (1-5 minutes)
[EVIDENCE] "Let me prove it - I'll build this with just a skill...
            [DEMO: Building, testing, showing results]"
   ↓ (5-30 seconds)
[RESOLUTION] "Boom! Same functionality. No MCP required. See?"
```

### Constraints

- **Minimum duration**: 60-300 seconds
- **Maximum gap between beats**: 5 minutes
- **Clip strategy**: Include ALL required beats, even if spread across time

---

## Template 2: TUTORIAL

**Use case**: How-to content, step-by-step demonstrations

### Required Beats

| Beat | Description | Minimum | Score Boost |
|------|-------------|---------|-------------|
| GOAL | What we're trying to achieve | YES | +4 |
| STEPS | The actual process/demonstration | YES | +15 |
| RESULT | The finished outcome | YES | +8 |

### Optional Beats

| Beat | Description | Score Boost |
|------|-------------|-------------|
| PREREQS | What you need first | +2 |
| TROUBLESHOOT | Common issues/gotchas | +3 |

### Detection Signals

**GOAL patterns:**
- "Let's build...", "I want to show you...", "Today we're going to..."
- "The goal is...", "We need to...", "I'm going to set up..."
- Statement of intent before action

**STEPS patterns:**
- Sequential actions with "First...", "Next...", "Then...", "Now..."
- Tool usage, code writing, configuration
- Live coding, terminal commands, UI interactions
- "So I'll...", "Let me just...", "What I'm doing here is..."

**RESULT patterns:**
- "And there we go...", "It works!", "Done"
- "Perfect", "There it is", "That's it"
- Showing the completed thing working
- Success/failure reactions

### Example Match

```
[GOAL] "Let's set up Playwright MCP from scratch"
   ↓
[PREREQS] "You'll need Node.js installed"
   ↓ (1-10 minutes)
[STEPS] "First, install the package... Now configure... Finally..."
   ↓
[TROUBLESHOOT] "If you get a timeout error, increase this value"
   ↓
[RESULT] "And there we go, browser automation working perfectly"
```

### Constraints

- **Minimum duration**: 90-300 seconds
- **Clip strategy**: Can summarize STEPS if too long, but MUST include GOAL and RESULT
- **STEPS can be condensed** for compilations (key moments only)

---

## Template 3: DISCOVERY

**Use case**: Finding something new, "check this out" moments

### Required Beats

| Beat | Description | Minimum | Score Boost |
|------|-------------|---------|-------------|
| FIND | The discovery itself | YES | +6 |
| EXPLORE | Investigating the discovery | YES | +10 |
| VERDICT | Assessment of the discovery | YES | +6 |

### Optional Beats

| Beat | Description | Score Boost |
|------|-------------|-------------|
| CONTEXT | Why this matters / prior frustration | +3 |
| COMPARISON | How it compares to alternatives | +3 |

### Detection Signals

**FIND patterns:**
- "Just found...", "Check this out...", "Look at this..."
- "Someone mentioned...", "I stumbled on..."
- Tool/product name introduction
- "Have you seen...?", "Did you know about...?"

**EXPLORE patterns:**
- "Let's see...", "Let me try...", "What does this do..."
- Testing, experimenting, clicking around
- "Interesting...", "Whoa...", discovery reactions
- "So if I do this..."

**VERDICT patterns:**
- "This is actually good/bad...", "I'm impressed..."
- "This might actually...", "I think I'll use this..."
- Clear judgment or recommendation
- "Worth it/not worth it", "Game changer/overrated"

### Example Match

```
[CONTEXT] "I've been frustrated with Cursor's speed lately"
   ↓
[FIND] "Someone in chat mentioned this new tool called Augment"
   ↓ (30 seconds - 3 minutes)
[EXPLORE] "Let me install it and see... okay running a test prompt..."
   ↓
[COMPARISON] "Whoa, that's way faster than Cursor"
   ↓
[VERDICT] "This might actually replace my main editor"
```

### Constraints

- **Minimum duration**: 45-180 seconds
- **EXPLORE can be condensed** for long explorations
- **FIND and VERDICT are essential** - never skip these

---

## Template 4: COMPARISON

**Use case**: A vs B content, evaluations, benchmarks

### Required Beats

| Beat | Description | Minimum | Score Boost |
|------|-------------|---------|-------------|
| CONTENDERS | The things being compared | YES | +4 |
| CRITERIA | What we're measuring | YES | +3 |
| TEST | Actual comparison | YES | +12 |
| WINNER | The conclusion/verdict | YES | +6 |

### Optional Beats

| Beat | Description | Score Boost |
|------|-------------|-------------|
| NUANCE | "It depends" situations | +2 |

### Detection Signals

**CONTENDERS patterns:**
- Two or more tools/approaches named
- "vs", "versus", "compared to", "or"
- "A vs B", "X compared to Y"

**CRITERIA patterns:**
- "Let's test...", "In terms of...", "For..."
- Specific metrics: "speed", "accuracy", "ease of use"
- "What I care about is..."

**TEST patterns:**
- Running both, showing results
- Side-by-side demonstration
- "First X... now Y..."
- Benchmark execution

**WINNER patterns:**
- "X wins", "I prefer...", "The better option is..."
- Clear recommendation
- "Go with X if you want..."

### Example Match

```
[CONTENDERS] "Claude Sonnet 4 vs GPT-4o for coding"
   ↓
[CRITERIA] "Testing on this complex refactor task"
   ↓ (1-5 minutes)
[TEST] "Sonnet's output... okay now GPT-4o... interesting"
   ↓
[WINNER] "Sonnet handled the edge cases better, clear winner here"
   ↓
[NUANCE] "Though for quick scripts, GPT-4o's speed might matter more"
```

### Constraints

- **Minimum duration**: 60-300 seconds
- **TEST can show highlights** rather than full runs
- **All other beats required** for completeness

---

## Template 5: PROBLEM-SOLUTION

**Use case**: Debugging, troubleshooting, overcoming obstacles

### Required Beats

| Beat | Description | Minimum | Score Boost |
|------|-------------|---------|-------------|
| PROBLEM | The issue/blocker | YES | +4 |
| INSIGHT | The aha moment/realization | YES | +8 |
| FIX | The solution applied | YES | +10 |
| CONFIRMATION | It works now | YES | +6 |

### Optional Beats

| Beat | Description | Score Boost |
|------|-------------|-------------|
| STRUGGLE | Failed attempts (adds drama) | +3 |

### Detection Signals

**PROBLEM patterns:**
- "Error", "Not working", "Broken", "Bug"
- Frustration, confusion
- "Why is this...", "What the hell...", "This should work..."
- Error messages, stack traces

**STRUGGLE patterns:**
- "Let me try...", "Maybe if I..."
- Failed attempts, dead ends
- "That didn't work either..."

**INSIGHT patterns:**
- "Wait...", "Oh!", "I think I see..."
- "The issue is...", "I bet it's..."
- Realization moment, aha!

**FIX patterns:**
- Actual fix applied
- Code change, configuration update
- "Let me change this to..."

**CONFIRMATION patterns:**
- "Yes!", "Finally!", "There we go"
- Working state demonstrated
- Relief, celebration

### Example Match

```
[PROBLEM] "Why is this MCP timing out? This should work..."
   ↓ (optional)
[STRUGGLE] "Let me check the config... no that's fine... maybe the port?"
   ↓
[INSIGHT] "Wait, I bet the issue is the connection timeout is too low"
   ↓
[FIX] "Let me bump this to 30 seconds..."
   ↓
[CONFIRMATION] "YES! There we go, it's connecting now"
```

### Constraints

- **Minimum duration**: 45-180 seconds
- **STRUGGLE is optional** but adds value/drama
- **CONFIRMATION is essential** - needs closure

---

## Scoring System

### Demo-First Prioritization

Complete demonstrations score significantly higher than verbal claims:

| Content Type | Base Score |
|--------------|------------|
| Complete demo (STEPS/EVIDENCE/TEST/FIX) | +15 |
| Result moment (RESOLUTION/RESULT/CONFIRMATION) | +8 |
| Discovery/insight moment | +6 |
| Verbal claim without demo | +4 |
| Context/setup | +2 |

### Template Match Scoring

```
template_score = (found_required_beats / total_required_beats) * base_weight
                 + (found_optional_beats / total_optional_beats) * 0.3
                 + temporal_coherence_bonus
                 - gap_penalty

Where:
- base_weight: 1.0 for complete required beats, 0.0 if any required beat missing
- temporal_coherence_bonus: +0.1 if beats appear in expected order
- gap_penalty: -0.05 per minute of gap between beats (max -0.3)
```

### Match Thresholds

| Score | Status | Action |
|-------|--------|--------|
| >= 0.8 | STRONG MATCH | Extract as complete story arc |
| 0.5 - 0.79 | PARTIAL MATCH | Flag for review, suggest missing beats |
| < 0.5 | NO MATCH | Fall back to individual moment detection |

---

## Gap Handling

When beats are separated by significant time:

| Gap Duration | Strategy |
|--------------|----------|
| < 60 seconds | Include everything between beats |
| 60-180 seconds | Include beats + 5s buffer, mark as "compilation" |
| > 180 seconds | Extract as separate clips with "[Part 1]" "[Part 2]" labeling |

---

## Validation Rules

### Strict Mode (ARGUMENT, COMPARISON)

All required beats MUST be present. If any are missing:
1. Search harder in the surrounding content
2. Flag as incomplete if not found
3. Do NOT extract as story arc without all required beats

### Flexible Mode (DISCOVERY, TUTORIAL, PROBLEM-SOLUTION)

Allow extraction with 66% of required beats:
- Extract with warnings about missing beats
- Apply confidence penalty: -0.1 per missing beat
- Still prioritize complete arcs over partial ones

---

## Integration with Existing Categories

Story arcs enhance, not replace, existing categories:

| Existing Category | Often Part Of |
|-------------------|---------------|
| reaction | RESOLUTION, CONFIRMATION, VERDICT |
| tip | EVIDENCE (in ARGUMENT), STEPS (in TUTORIAL) |
| teaching | STEPS, EVIDENCE, EXPLORE |
| opinion | CLAIM, VERDICT, WINNER |
| story | PROBLEM-SOLUTION (natural narrative) |

When a segment matches both a category AND a story arc beat, include both:
- Category for standalone clip value
- Beat role for narrative completeness
