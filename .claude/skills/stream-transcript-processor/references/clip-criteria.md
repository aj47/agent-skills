# Clip Criteria Reference

What makes a good techfren clip for TikTok, Instagram Reels, YouTube Shorts, and similar platforms.

---

## Clip Value Signals

### Discovery Moments (Highest Value)
**Score: +4 per signal**

These create "I need to try this" reactions:

- Tool mentions with specific results
- "Just found this..." energy
- Trending/viral indicators
- Specific metrics (stars, downloads, speed)
- First-time discoveries

**Examples from transcripts:**
> "Dude, this has 20K stars on GitHub and I've never heard of it"

> "Just discovered this runs completely locally, no API needed"

### Authentic Reactions (High Value)
**Score: +3 per signal**

Real emotional moments that feel genuine:

- Natural surprise ("whoa", "wait")
- Genuine excitement ("dude", "sick", "boom")
- Satisfaction ("there we go", "perfect")
- Discovery ("that's actually...", "oh")

**What makes it authentic:**
- Unscripted feel
- Matches the result/discovery
- Not forced or performative

### Value Propositions (Medium-High Value)
**Score: +2 per signal**

Benefits that resonate with tech audience:

| Value Prop | Why It Works |
|------------|--------------|
| Free | Budget-conscious devs |
| Open source | Trust, transparency |
| Local/offline | Privacy, speed |
| No installation | Low friction |
| No signup | Immediate value |
| Fast | Time savings |

**Stack multiple value props when possible:**
> "Free. Open source. Runs locally."

### Result Moments (Medium-High Value)
**Score: +3 per signal**

Proof that something works:

- Successful completions
- Before/after comparisons
- Metric improvements
- "It worked" moments

**Examples:**
> "Boom, there we go. It just generated the entire component."

> "Went from 500ms to 50ms load time. Just by switching to this."

### Tool Demonstrations (Medium Value)
**Score: +1-2 per signal**

Showing tools in action:

- Live testing on stream
- "Let's see if..." moments
- Real-world use cases
- Problem-solving with tools

---

## Optimal Clip Lengths

| Platform | Ideal Length | Max Length |
|----------|--------------|------------|
| TikTok | 30-45 seconds | 60 seconds |
| Instagram Reels | 30-45 seconds | 60 seconds |
| YouTube Shorts | 45-60 seconds | 60 seconds |
| X/Twitter Video | 30-45 seconds | 60 seconds |

**For longer clips (2-3 min):**
- Complete tutorials
- Full problem-solution arcs
- Compilation of related moments

---

## Scoring Thresholds

Calculate total score from signals:

| Score | Priority | Action |
|-------|----------|--------|
| 8+ | **High** | Definitely clip - viral potential |
| 5-7 | **Medium** | Good clip - worth extracting |
| 3-4 | **Low** | Consider if needed for content |
| 1-2 | **Skip** | Not clip-worthy |

---

## Clip Structure Requirements

### Hook (First 3 Seconds)
- Must grab attention immediately
- Bold claim or surprising result
- No slow builds or context

**Good hooks:**
> "This tool just replaced my entire workflow."

> "Cursor completed the function in 2 seconds."

**Bad hooks (skip these):**
> "So I was trying this thing earlier..."

> "Hey what's up, today I want to show you..."

### Context Window

Always include setup for the payoff:

- 2-3 seconds before the peak moment
- Enough context to understand what happened
- Not so much that it drags

### Natural Boundaries

Clips must:
- Start at beginning of a sentence
- End at end of a sentence
- Include complete thoughts
- Be understandable standalone

---

## Skip Criteria

Do NOT clip moments that are:

### Content Issues
- **Off-topic**: Non-tech tangents, personal stories unrelated to tools
- **Incomplete**: Abandoned explorations, interrupted thoughts
- **Negative without resolution**: Complaints without solutions
- **Too vague**: Generic excitement without specifics

### Technical Issues
- **Poor audio**: Speaking away from mic, background noise
- **Mid-sentence**: Cuts off thoughts
- **Missing context**: References something not shown
- **Too short**: Under 15 seconds (not enough context)

### Engagement Issues
- **No hook**: Starts slow, no grabbing first line
- **No payoff**: Builds up but no satisfying result
- **Repetitive**: Same point as another clip

---

## Compilation Criteria

When to create compilations (multiple segments combined):

### Good Compilation Topics
- Complete tutorials from scattered segments
- Before/after comparisons
- Multiple tools in same category
- Problem-solving journey

### Compilation Rules
- Minimum 2 segments on same topic
- Segments should flow logically
- Remove gaps between segments
- Total duration can exceed single clip limits (2-5 min)

---

## MrBeast Principles Applied

From content analysis research:

### 1. Hook Priority
- First 3 seconds decide if viewer stays
- Start with result, not setup
- Bold claims outperform questions

### 2. Retention Patterns
- Re-hook every 15-30 seconds
- Avoid dead air or slow moments
- Stack value props quickly

### 3. Wow Factor
- Include surprising result or comparison
- Specific numbers beat vague claims
- Show, don't just tell

### 4. CTA Timing
- Action CTAs ("try it", "download") at end
- Never mid-clip engagement asks
- Link in bio/reply, not in video

---

## Quality Checklist

Before finalizing a clip:

- [ ] Hook is in first 3 seconds
- [ ] First word is NOT: so, hey, I, what's up, alright
- [ ] Contains specific tool or result
- [ ] Includes at least one value prop if applicable
- [ ] Has authentic reaction (if reaction clip)
- [ ] Starts at sentence beginning
- [ ] Ends at sentence end
- [ ] Understandable without prior context
- [ ] Duration is within platform limits
- [ ] Not duplicate of another clip

---

## Example Clip Evaluations

### High Score (8+) - Clip This
```
[00:45:23] "Dude, this is insane. Cursor just completed the entire
authentication flow in like 2 seconds. It's completely free and
open source. Let me show you—boom, there we go, done."
```
**Signals:** dude (+3), insane (+3), Cursor (+1), 2 seconds (+3), free (+2), open source (+2), boom (+3)
**Total: 17** - Definitely clip

### Medium Score (5-7) - Consider
```
[01:12:45] "Okay let's try this new tool I found. Pretty cool,
it runs locally which is nice. Let's see if it works..."
```
**Signals:** let's try (+2), locally (+2), pretty cool (+2)
**Total: 6** - Worth considering, needs strong visual/result

### Low Score (1-2) - Skip
```
[02:30:12] "So I was thinking about this earlier and I kind of
want to maybe try setting up the thing we talked about..."
```
**Signals:** None detected
**Total: 0** - Skip (slow start, hedging, no specifics)

---

## Integration Note

For clip extraction, use the existing clipper skill:
- [clipper/SKILL.md](../../clipper/SKILL.md) - Full extraction workflow
- [clipper/SEGMENT_TYPES.md](../../clipper/SEGMENT_TYPES.md) - Detailed category criteria
