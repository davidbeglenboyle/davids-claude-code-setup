---
name: review-loop
description: "Run quality verification and review loop on session deliverables. Detects organisation from context and applies appropriate review standards. Manually invoked only."
---

# Review Loop: Quality Verification and Critique Cycle

Run a structured quality loop on deliverables from the current session. This skill is manually invoked — it never runs automatically.

## When to Use

Invoke with `/review-loop` or when the user asks to "quality check", "review loop", or "run the review cycle" on deliverables.

## The Loop (max 3 rounds)

### Step 1: Identify Deliverables

Find files created or modified in this session with deliverable extensions: `.md`, `.docx`, `.txt`, `.pdf`, `.pptx`, `.xlsx`.

If no deliverables found, ask the user which files to review.

### Step 2: Verify (quality-score)

Run `quality-score [filepath]` on each deliverable using the Bash tool.

* If `quality-score` is not installed (`~/bin/quality-score` not found), skip to Step 3
* If score >= 80, proceed to Step 3
* If score < 80, fix the reported issues (unresolved brackets, TODOs, naming issues) and re-run quality-score
* If exit code 2 (auto-fail), stop the loop and report to the user immediately

### Step 3: Review (critic or devils-advocate)

Detect the context from the deliverable — file content, project folder name, conversation history, or explicit user instruction.

<!-- CUSTOMISE: Replace with your own organisation detection logic.
     For example, if you work across multiple clients with different brand standards,
     you might detect the client from file content or folder names and route to
     different review agents.

     Example routing:
     - Client A work → launch deliverable-critic agent with Client A standards
     - Client B work → launch deliverable-critic agent with Client B standards
     - Internal work → run /devils-advocate
     - Unclear → ask the user
-->

**Branded client work:**
Launch the deliverable-critic agent via the Task tool (subagent_type=general-purpose). Pass the file path and specify the organisation context. The agent file is at `~/.claude/agents/deliverable-critic.md` — include its full content in the agent prompt.

**Internal or general work:**
Run the `/devils-advocate` skill on the deliverable.

**Unclear:**
Ask the user which standards to apply.

### Step 4: Fix

**For critic agent findings:**
Launch the deliverable-fixer agent via the Task tool (subagent_type=general-purpose). Pass the file path and the critic's findings. The agent file is at `~/.claude/agents/deliverable-fixer.md` — include its full content in the agent prompt.

**For devils-advocate findings:**
Fix in the main session. Address the strongest concern first, then work through remaining challenges.

### Step 5: Re-score

Run `quality-score [filepath]` again.

* Score >= 80 → deliverable is done
* Score < 80 and rounds < 3 → return to Step 4
* Rounds = 3 → stop and present remaining issues to the user for manual decision

### Step 6: Report

Show the user:
* Final quality-score output for each deliverable
* Summary of what was fixed
* Any remaining issues that need manual attention

## Rules

* **Maximum 3 total rounds** (the initial implement does not count; rounds start at Step 4)
* **Auto-fail (exit code 2) stops immediately** — report to user, do not attempt fixes
* **Always show the final quality-score output** — the user should see the score
* **If the user says "skip review"**, run only quality-score without the critic/devils-advocate step
* **Do not modify files the user did not create in this session** unless explicitly asked
* **The critic agent is read-only** — it produces findings but cannot edit. The fixer agent applies changes
