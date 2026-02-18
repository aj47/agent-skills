---
name: codex-issue-runner
description: "Runs OpenAI Codex CLI agents in iTerm slots to work on GitHub issues. Use when asked to 'run codex on an issue', 'assign an issue to codex', 'spin up a codex agent', or 'have codex work on issue #N'."
---

# Codex Issue Runner

## Overview
Automates spinning up OpenAI Codex CLI agents in SpeakMCP workspace slots to work on GitHub issues and PRs. Each slot is an independent workspace that can run one Codex agent at a time.

## Slot Architecture
- Slots are at `/Users/ajjoobandi/Development/SpeakMCP-Workspaces/slot-N` (N=1 to 5)
- Each slot is a git clone of the SpeakMCP repo
- Max 5 concurrent Codex agents

## Workflow

### Step 1: Identify Available Slots
Use `iterm:list_sessions` to see which slots are occupied. Look for session names containing `slot-N`.

### Step 2: Prepare the Slot
If the slot doesn't have an iTerm window, create one with `iterm:create_window`.
Navigate to the slot directory and reset to main:
```
cd ~/Development/SpeakMCP-Workspaces/slot-N
gitcm
```
The `gitcm` alias runs `git fetch && git checkout main && git pull`.

### Step 3: Launch Codex
Type `codex` and press ENTER in the terminal. Wait for the Codex UI to appear (look for the prompt box with model info).

### Step 4: Submit the Task
Write a clear task description referencing the issue number. Always instruct Codex to read the full issue first:
```
Work on issue #N - [brief description]. First read the issue by running `gh issue view N` to get full context, then implement the fix.
```
Press ENTER to submit.

### Step 5: Verify Submission
Wait 2-3 seconds, then read terminal output to confirm Codex is working (look for "Working" status).

## Task Formatting Tips
- Always tell Codex to read the issue/PR first with `gh issue view N` or `gh pr view N`
- Give a one-line summary so Codex has initial context
- For PRs, use `gh pr view N` and `gh pr diff N` to understand existing changes

## Monitoring
- Use `iterm:read_terminal_output` with the session ID to check progress
- Codex shows "Working (Ns)" while processing
- Press ESC to interrupt if needed

## After Codex Finishes
Codex will make changes locally. You may want to:
1. Review changes: `git diff`
2. Create a branch: `git checkout -b fix/issue-N-description`
3. Commit and push: `git add . && git commit -m "fix: description" && git push`
4. Create PR: `gh pr create --title "Fix #N: description" --body "Closes #N"`
Or run `www "description"` which automates the PR workflow.

## Common Issues
- If Codex fails to connect to GitHub, check internet connection
- If slot is dirty, run `git stash` or `git reset --hard` before `gitcm`
- If Codex hangs, press ESC and retry
