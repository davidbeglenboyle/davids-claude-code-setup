---
name: edit
description: |
  Spatial editing for Markdown files. Process inline edit instructions marked
  with {curly braces}. Use when: user runs /edit, asks to "process my edit
  markers", "apply my inline comments", or mentions {braces} editing workflow.
  Replaces copy-paste-to-Claude with "leave instructions where they belong."
invocation: user
---

# /edit — Spatial Editing for Markdown

Process inline edit instructions marked with `{curly braces}` in Markdown files.

## Workflow

### 1. DISCOVER files

Parse the skill arguments to find target files:

- **If file paths provided** (e.g., `/edit draft.md` or `/edit draft.md notes.md`): use those files
- **If directory provided** (e.g., `/edit ./posts/`): scan that directory for `.md` files containing `{instructions}`
- **If no arguments**: Ask the user which file or directory to process

### 2. FIND edit instructions

Run the helper script to locate all `{instruction}` markers:

```bash
bash ~/.claude/skills/edit/scripts/find-edits.sh [file-or-directory]
```

This outputs lines like:
```
draft.md:12:{feels too abstract}
draft.md:28:{make this hit harder}
draft.md:45:{don't say simple, show it}
```

### 3. PRESENT the plan

Show the user what you found:

```
Found 3 edit instructions in draft.md:

1. Line 12: {feels too abstract}
2. Line 28: {make this hit harder}
3. Line 45: {don't say simple, show it}

Proceed with edits?
```

Wait for user approval before continuing.

### 4. APPLY edits

For each `{instruction}`:

1. Read the **whole file** to understand context (document flow, tone, structure)
2. Identify the text surrounding the `{instruction}` marker
3. Apply the edit instruction to improve that text
4. **Remove the `{braces}` and instruction** from the output — only the improved text remains
5. Use the Edit tool to make the change

### 5. REPORT results

After all edits, show a diff summary:

```
## Edit Results

### Line 12: {feels too abstract}
**Before:** The system processes data efficiently.
**After:** The system crunches 10,000 records per second, turning raw logs into actionable alerts.

### Line 28: {make this hit harder}
**Before:** This approach saves time.
**After:** This approach claws back three hours every week — time you're currently losing to manual reconciliation.

### Line 45: {don't say simple, show it}
**Before:** The setup process is simple.
**After:** Setup takes four clicks: connect, configure, test, deploy.
```

## Key Behaviours

- **Each `{brace}` is independent** — process them one at a time
- **Whole-file context** — read the entire document to maintain consistency
- **No backup created** — rely on git for version control
- **Braces disappear** — the `{instruction}` marker is always removed, leaving only improved text

## Example

**Input file:**
```markdown
# Product Launch

We're excited to announce our new feature. {too corporate, make it punchy}

This tool helps teams collaborate better. {vague - what specifically does it do?}
```

**After /edit:**
```markdown
# Product Launch

Your deploy just got a turbo button.

This tool syncs design files across Figma, Slack, and GitHub in real-time — no more "which version is latest?" conversations.
```

## Edge Cases

- **Nested braces**: Treat `{outer {inner} text}` as a single instruction (rare, handle gracefully)
- **Code blocks**: Skip `{braces}` inside fenced code blocks (``` or ~~~) — these are likely code, not instructions
- **Empty braces**: Skip `{}` with no content
- **Very long instructions**: Still process them — the user knows what they want
