# Beat Detection Patterns

Detailed patterns for detecting narrative beats in transcriptions. Use these patterns during analysis to identify story arc components.

## Beat Detection Overview

For each sentence/segment, scan for beat markers. When a beat is detected:
1. Record the beat type
2. Note the sentence indices (start/end)
3. Extract the key phrase that triggered detection
4. Assign confidence based on pattern strength

---

## CLAIM Beats

Claims are thesis statements, assertions, or opinions that set up an argument.

### High Confidence Patterns (0.85+)

```
"My thesis is..."
"The argument here is..."
"I'm going to prove that..."
"Here's what I believe..."
"Unpopular opinion:..."
"Hot take:..."
"The truth is..."
"Here's the thing..."
"What most people don't realize is..."
```

### Medium Confidence Patterns (0.70-0.84)

```
"I think..." + [strong assertion]
"I honestly think..."
"I really believe..."
"[Tool/Concept] can..." + [capability claim]
"[Tool/Concept] is better than..."
"People say X but actually..."
"Contrary to popular belief..."
"The problem with X is..."
```

### Low Confidence Patterns (0.60-0.69)

```
"I think..." + [mild opinion]
"Probably..."
"In my experience..."
"From what I've seen..."
```

### Context Signals

CLAIM beats are often preceded by:
- Topic introductions ("So let's talk about...")
- Questions from audience ("Someone asked about...")
- Transition phrases ("Now, here's where it gets interesting...")

### Example Detections

| Sentence | Pattern Match | Confidence |
|----------|---------------|------------|
| "My thesis today is that skills can completely replace MCPs" | "My thesis is..." + capability claim | 0.92 |
| "I honestly think Cursor is overrated" | "I honestly think" + strong opinion | 0.78 |
| "The truth is, most people are doing this wrong" | "The truth is..." | 0.88 |

---

## EVIDENCE Beats

Evidence demonstrates, proves, or supports a claim through action.

### High Confidence Patterns (0.85+)

```
"Let me prove it..."
"Let me demonstrate..."
"Watch this..."
"I'll show you..."
"Here's the proof..."
"Let me actually do it..."
"So I'm going to build/create/make..."
[Terminal command execution]
[Code being written/run]
[Live demo of feature]
```

### Medium Confidence Patterns (0.70-0.84)

```
"Let me try..."
"So if I..."
"Check this out..."
"Here's what happens when..."
"So I'll just..."
"Let me just..."
```

### Behavioral Signals

Evidence beats are characterized by:
- **Action language**: Active verbs (building, coding, testing, running)
- **Duration**: Typically 1-10 minutes of sustained activity
- **Tool mentions**: Specific tools being used
- **Step narration**: "First I...", "Now I...", "Next..."

### Demo Detection Heuristics

A segment is likely a demo if it has 3+ of these:
1. Multiple sentences with action verbs
2. Technical tool/command mentions
3. "Let me..." or "I'll..." phrases
4. Sequential markers (first, then, now, next)
5. Duration > 60 seconds of continuous related content

### Example Detections

| Sentences | Pattern Match | Confidence |
|-----------|---------------|------------|
| "Let me prove it. I'm going to build this with just a skill. First, I'll create the file..." | "Let me prove it" + sequential actions | 0.90 |
| "Watch this. So I'm running the command now..." | "Watch this" + action | 0.85 |
| "So if I type this here... and then run it..." | "So if I" + actions | 0.75 |

---

## RESOLUTION Beats

Resolution confirms or denies the original claim, showing the outcome.

### High Confidence Patterns (0.85+)

```
"See?"
"There you go!"
"It worked!"
"Boom!"
"That proves..."
"And that's why..."
"Done!"
"There it is!"
"[Success exclamation] + [callback to claim]"
```

### Medium Confidence Patterns (0.70-0.84)

```
"And there we have it..."
"So yeah, that's..."
"Which shows that..."
"Perfect!"
"Nice!"
```

### Emotional Signals

Resolution beats often have:
- High energy/excitement
- Exclamation marks
- Callback to original claim
- Satisfaction/relief tone
- "I told you" energy

### Validation Rule

A resolution is valid if:
1. It comes AFTER an EVIDENCE beat
2. It references or implies the original CLAIM
3. It has conclusive language (not tentative)

### Example Detections

| Sentence | Pattern Match | Confidence |
|----------|---------------|------------|
| "Boom! Same functionality. No MCP required. See?" | "Boom" + "See?" + claim callback | 0.95 |
| "And that proves skills can do what MCPs do" | "That proves" + claim callback | 0.90 |
| "There we go, it's working perfectly now" | "There we go" + success confirmation | 0.82 |

---

## GOAL Beats

Goals state the objective of a tutorial or demonstration.

### High Confidence Patterns (0.85+)

```
"Today we're going to..."
"Let's build..."
"I want to show you how to..."
"The goal is..."
"We're going to set up..."
"I'm going to walk you through..."
"Let me teach you..."
```

### Medium Confidence Patterns (0.70-0.84)

```
"So I want to..."
"What I'm trying to do is..."
"The plan is..."
"I need to..."
```

### Context Signals

GOAL beats typically appear:
- At the beginning of a topic segment
- After topic transitions
- Following audience questions
- With future tense language

### Example Detections

| Sentence | Pattern Match | Confidence |
|----------|---------------|------------|
| "Let's set up Playwright MCP from scratch" | "Let's set up..." | 0.88 |
| "Today we're going to build a video clipper skill" | "Today we're going to..." | 0.92 |
| "I want to show you how to configure this properly" | "I want to show you how to..." | 0.85 |

---

## STEPS Beats

Steps are the actual tutorial/demo content - sequential actions.

### Sequential Markers

```
"First..."
"Then..."
"Next..."
"Now..."
"After that..."
"Step one/two/three..."
"The first thing..."
"Once that's done..."
```

### Action Language

```
"I'll..."
"Let me..."
"So I'm going to..."
"What I'm doing here is..."
"Now I need to..."
```

### Duration Signals

STEPS beats are typically:
- 1-10 minutes long
- Multiple sentences with related actions
- Progressive (each step builds on previous)
- Tool-focused content

### Grouping Logic

Consecutive sentences with step markers should be grouped:
- Same topic = same STEPS beat
- Topic change = new STEPS beat or end of tutorial

### Example Detection

```
Sentence 45: "First, we need to install the package"
Sentence 46: "npm install playwright-mcp"
Sentence 47: "Now let's configure it"
Sentence 48: "Open your config file..."
Sentence 49: "Add this section here..."

→ STEPS beat: indices 45-49, duration ~2 minutes
```

---

## RESULT Beats

Results show the completed outcome of a tutorial.

### High Confidence Patterns (0.85+)

```
"And there we go!"
"It works!"
"Done!"
"That's it!"
"Perfect!"
"There it is!"
"Finished!"
"And now it's working"
```

### Medium Confidence Patterns (0.70-0.84)

```
"So now we have..."
"And that gives us..."
"Alright, so..."
"Success!"
```

### Behavioral Signals

RESULT beats often include:
- Demonstrating the working thing
- Satisfaction expressions
- "Ta-da" energy
- Summary of what was accomplished

---

## FIND Beats

Discovery of something new.

### High Confidence Patterns (0.85+)

```
"Just found..."
"Check this out..."
"Have you seen...?"
"I just discovered..."
"Someone showed me..."
"I stumbled on..."
"Look what I found..."
```

### Medium Confidence Patterns (0.70-0.84)

```
"There's this new..."
"Someone mentioned..."
"I heard about..."
"Apparently there's..."
```

### Context Signals

FIND beats often include:
- Tool/product name (first mention)
- Excitement/curiosity tone
- "New" or "just" language
- Link or reference sharing

---

## EXPLORE Beats

Investigation and experimentation with a discovery.

### High Confidence Patterns (0.85+)

```
"Let's see..."
"Let me try..."
"What does this do?"
"So if I..."
"Let me test..."
"I wonder if..."
```

### Behavioral Signals

- Testing, clicking, experimenting
- Running commands
- Asking questions while investigating
- "Interesting...", "Whoa...", "Hmm..."
- Multiple attempts or tests

---

## VERDICT Beats

Assessment or judgment of a discovery.

### High Confidence Patterns (0.85+)

```
"This is actually really good"
"I'm impressed"
"Not impressed"
"This might replace..."
"I think I'll use this"
"Worth it / Not worth it"
"Game changer"
"Overrated / Underrated"
```

### Medium Confidence Patterns (0.70-0.84)

```
"I like this because..."
"The problem is..."
"It's okay but..."
"Decent but not great"
```

---

## PROBLEM Beats

Statement of an issue or blocker.

### High Confidence Patterns (0.85+)

```
"Error..."
"It's not working"
"What the hell?"
"Why is this...?"
"This should work but..."
"Bug..."
"Broken..."
"It keeps failing"
```

### Emotional Signals

- Frustration
- Confusion
- Surprise (negative)
- Expletives (context-dependent)

---

## INSIGHT Beats

The "aha" moment of realization.

### High Confidence Patterns (0.85+)

```
"Wait..."
"Oh!"
"I think I see the problem"
"The issue is..."
"I bet it's..."
"That's the problem!"
"Aha!"
"I figured it out"
```

### Behavioral Signals

- Pause followed by realization
- Tone shift from frustrated to understanding
- "The reason is..." language
- Connecting dots

---

## FIX Beats

Application of a solution.

### High Confidence Patterns (0.85+)

```
"Let me change this to..."
"If I fix this..."
"The solution is..."
"I need to update..."
"Let me try..."  (after INSIGHT)
```

### Behavioral Signals

- Code/config modification
- Following INSIGHT immediately
- Targeted action (not exploration)

---

## CONFIRMATION Beats

Verification that the fix worked.

### High Confidence Patterns (0.85+)

```
"Yes!"
"Finally!"
"It's working now!"
"There we go!"
"Fixed!"
"That did it!"
```

### Emotional Signals

- Relief
- Celebration
- Satisfaction
- "I told you" energy

---

## CONTENDERS Beat

Introduction of items being compared.

### High Confidence Patterns (0.85+)

```
"X vs Y"
"X versus Y"
"Comparing X and Y"
"X compared to Y"
"Let's see how X stacks up against Y"
"Which is better, X or Y?"
```

---

## CRITERIA Beat

What's being measured in a comparison.

### High Confidence Patterns (0.85+)

```
"Let's test for..."
"In terms of..."
"What I care about is..."
"The criteria are..."
"I'm looking at..."
```

---

## TEST Beat

Actual comparison execution.

### Behavioral Signals

- Running both options
- Side-by-side demonstration
- "First X... now Y..."
- Benchmark results
- Timing/measuring

---

## WINNER Beat

Conclusion of comparison.

### High Confidence Patterns (0.85+)

```
"X wins"
"I prefer X"
"The winner is..."
"Go with X if..."
"X is better because..."
"Clear winner here"
```

---

## Cross-Beat Relationships

### Required Sequences

| Template | Required Sequence |
|----------|-------------------|
| ARGUMENT | CLAIM → EVIDENCE → RESOLUTION |
| TUTORIAL | GOAL → STEPS → RESULT |
| DISCOVERY | FIND → EXPLORE → VERDICT |
| COMPARISON | CONTENDERS → TEST → WINNER |
| PROBLEM-SOLUTION | PROBLEM → INSIGHT → FIX → CONFIRMATION |

### Beat Proximity Rules

| From | To | Max Gap |
|------|-----|---------|
| CLAIM | EVIDENCE | 5 minutes |
| EVIDENCE | RESOLUTION | 2 minutes |
| GOAL | STEPS | 1 minute |
| STEPS | RESULT | 2 minutes |
| FIND | EXPLORE | 2 minutes |
| EXPLORE | VERDICT | 3 minutes |
| INSIGHT | FIX | 30 seconds |
| FIX | CONFIRMATION | 1 minute |

---

## Orphan Beat Detection

An **orphan beat** is a beat without its required companions:

| Beat Type | Is Orphan If Missing |
|-----------|---------------------|
| CLAIM | No EVIDENCE within 5 minutes |
| EVIDENCE | No CLAIM before OR no RESOLUTION after |
| RESOLUTION | No EVIDENCE before |
| GOAL | No STEPS or RESULT after |
| FIND | No VERDICT after |

### Orphan Handling

1. **Flag** orphan beats in validation report
2. **Search harder** for missing companion beats
3. If still missing, **extract as standalone** with warning
4. **Log** for manual review

---

## Confidence Calculation

For each detected beat:

```
beat_confidence = pattern_strength * context_bonus * sequence_bonus

Where:
- pattern_strength: 0.60-0.95 based on pattern matched
- context_bonus: 1.0-1.2 if surrounding content supports
- sequence_bonus: 1.0-1.15 if beat appears in expected position
```

### Minimum Thresholds

| Beat Type | Minimum Confidence |
|-----------|-------------------|
| EVIDENCE (demo) | 0.70 |
| All others | 0.60 |
