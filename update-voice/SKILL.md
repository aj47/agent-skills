---
name: update-voice
description: "Syncs AJ's voice guide from ~/.aj-voice.md to all skills and Claude project instructions. Use when asked to update voice, sync voice guide, or after editing ~/.aj-voice.md."
---

# Update Voice — Sync Source of Truth

## Overview
Single command to propagate AJ's voice guide from `~/.aj-voice.md` to:
1. All skill files that contain a voice section
2. Claude project instructions (via browser automation)

---

## Source of Truth
**File**: `~/.aj-voice.md`

Edit that file directly to update your voice. Then run this skill to push changes everywhere.

---

## Step 1: Read the current voice guide
```bash
cat ~/.aj-voice.md
```

---

## Step 2: Sync to Skills

Find all skills with a voice section and replace it:

```bash
SKILLS_DIR="/Users/ajjoobandi/Library/Application Support/app.speakmcp/skills"

# Skills known to contain voice content — add more as needed
VOICE_SKILLS=(
  "x-post-tweet"
  "x-feed-summarizer"
  "x-twitter-scraper"
)

for skill in "${VOICE_SKILLS[@]}"; do
  skill_file="$SKILLS_DIR/$skill/SKILL.md"
  if [ -f "$skill_file" ]; then
    echo "Checking $skill..."
    # The voice section in each skill is marked with:
    # <!-- VOICE_START --> ... <!-- VOICE_END -->
    # If markers exist, replace the content between them
    if grep -q "<!-- VOICE_START -->" "$skill_file"; then
      echo "  → Updating voice section in $skill"
      # Use Python for reliable multiline replacement
      python3 << PYEOF
import re, pathlib

voice_file = pathlib.Path.home() / ".aj-voice.md"
skill_path = "$skill_file"

voice_content = voice_file.read_text()
skill_content = pathlib.Path(skill_path).read_text()

# Replace between markers
new_section = f"<!-- VOICE_START -->\n{voice_content}\n<!-- VOICE_END -->"
updated = re.sub(
    r'<!-- VOICE_START -->.*?<!-- VOICE_END -->',
    new_section,
    skill_content,
    flags=re.DOTALL
)

pathlib.Path(skill_path).write_text(updated)
print(f"  ✓ Updated {skill_path}")
PYEOF
    else
      echo "  ⚠ No voice markers in $skill — skipping (add <!-- VOICE_START --> / <!-- VOICE_END --> markers)"
    fi
  fi
done
```

---

## Step 3: Sync to Claude Projects via Browser

Claude projects don't have an API — update via browser automation using the logged-in Chrome session.

```bash
# Check CDP available
curl -s --max-time 3 http://localhost:9222/json/version | head -c 50
```

Navigate to the Claude project that contains AJ's voice instructions:

```bash
agent-browser --cdp 9222 open https://claude.ai/projects
agent-browser --cdp 9222 wait 3000
agent-browser --cdp 9222 snapshot -i
```

Find the project (e.g. "TechFren Content" or similar), click it, then find the project instructions / custom instructions section and update it with the voice guide content.

**Typical flow:**
1. Snapshot to find project list
2. Click target project
3. Snapshot again — look for "Edit instructions", "Project instructions", or gear icon
4. Click the instructions textbox
5. Select all (Cmd+A) and replace with updated voice content
6. Save

---

## Step 4: Update personal-context skill

The `personal-context/aj47-profile.md` should also stay in sync with major voice changes:

```bash
echo "personal-context is profile/identity — voice is separate. Only update if identity changes."
```

---

## Adding Voice Markers to a Skill

To make a skill auto-syncable, add these markers around its voice section:

```markdown
## AJ's Voice Guide
<!-- VOICE_START -->
[voice content will be auto-replaced here]
<!-- VOICE_END -->
```

---

## Quick Update Workflow

```bash
# 1. Edit your voice
nano ~/.aj-voice.md  # or open in any editor

# 2. Run sync (invoke this skill)
# Agent reads ~/.aj-voice.md and updates all marked skill files + Claude projects
```

---

## Files Updated By This Skill
| Target | Method | Status |
|--------|--------|--------|
| `~/.aj-voice.md` | Manual edit | Source of truth |
| `skills/x-post-tweet/SKILL.md` | Marker replacement | Auto |
| `skills/x-feed-summarizer/SKILL.md` | Marker replacement | Auto |
| Claude Projects instructions | Browser automation | Semi-auto |

---

## Related Skills
- **x-post-tweet** — Uses voice guide for tweet composition
- **claude-projects-manager** — For navigating and editing Claude project instructions
- **chrome-debug-session** — CDP browser automation for Claude.ai
