# [Your Name] - Claude Code Preferences

## Professional Context

<!--
Add your professional background here. This helps Claude understand your expertise
and tailor responses appropriately.

Example:
[Your Name] is [role] at [company], working on [domains].
Background includes [relevant experience].
-->

### Current interests
<!--
What are you currently focused on? This helps Claude understand context.

Example:
* Topic area 1
* Topic area 2
* Topic area 3
-->

## Project Directory Structure

### README.md discipline
Every project has a README.md in the root. Whenever working on a project, always read the README.md first to understand what it's about. When making changes, update the README.md to reflect them.

### Primary working folder
* **Location:** `~/projects` <!-- Update to your location -->
* **Naming convention:** `YYYY-MM-DD-project-name-hyphenated`
* New tasks get a new project folder here unless otherwise specified
* When asked to work on "a project", list this folder first to find existing projects

### GitHub repos
* **Location:** `~/repos` <!-- Update to your location -->
* All GitHub repository work happens here

## Documentation Hierarchy

When multiple CLAUDE.md files exist, precedence is:

1. **User-level** (`~/.claude/CLAUDE.md`) — Global defaults, always applies
2. **Project-specific** (in repo root) — Overrides user-level for that project
3. **Sub-project** (nested directories) — Overrides parent for that scope

**Rules:**
* Project-specific files may contradict user-level guidance intentionally
* When in doubt, project-specific wins over global
* Cross-reference rather than duplicate — keep detail in one place

## Session Context Loading

When starting work on a complex or multi-session task:
1. **Recent notes** — Check for yesterday/today entries in your notes folder
2. **Project README** — Status, resume commands, next steps

Don't ask — just load what's relevant. Files are memory.

## Working Directory Rules

### Keep directories clean
* Working directories should only contain the most recent, relevant files
* Remove clutter proactively

### Archive policy
* When updating or replacing files (especially Markdown), archive the old version
* Move outdated files to an `/archive` subfolder
* Archive folders can accumulate — that's expected and fine

### Folder structure principle
For projects with scripts that produce outputs, separate by function:
```
project/
├── README.md          ← Overview and how to run
├── scripts/           ← Code that generates outputs
├── reports/           ← Generated outputs (intermediate)
├── summary/           ← Key findings (read first)
└── archive/           ← Superseded files
```

### Deliverables naming convention
When creating deliverables (emails, documents, proposals, exports):
* Use proper capitalisation with spaces, not hyphens
* Include date in brackets at the end
* Format: `Descriptive Name (19th Jan 2026).ext`

Examples:
* `Project Proposal (19th Jan 2026).docx`
* `Q1 Report Summary (3rd Feb 2026).md`

This applies to human-facing outputs. Source code uses `YYYY-MM-DD-hyphenated-name`.

## Context Engineering

### Descriptive markdown filenames
When creating markdown files, use filenames that summarise the content:
* **Good:** `api-429-errors-traced-to-rate-limits.md`
* **Avoid:** `notes.md`, `analysis.md`, `ideas.md`, `draft.md`

### First-line discipline
Every markdown file starts with a one-sentence summary. No preamble, no heading first.

Example:
```
This project extracts podcast listening patterns from API data.

## Overview
...
```

### README template for projects
Project READMEs follow this structure:
1. **One-sentence summary** (first line, no heading)
2. **Status** — Active / Paused / Complete, with date
3. **Key files** — What each important file does
4. **How to resume** — Commands or next steps

## Communication Preferences

### Tone and style
* Natural, conversational, matter-of-fact
* Humble — confident where warranted, never overconfident
* Professional yet plain — simple language over jargon
* High insight-to-word ratio — density matters more than length
* Challenge over agreement — improve thinking where needed

### Avoid
* Overly enthusiastic or embellished adjectives
* Fluff and superfluous material
* Excessive hedging
* Acronyms without explanation

### Formatting (longer responses)
* H1 (##) for main sections with Roman numerals (I, II, III)
* H2 (###) for subsections with letters (A, B, C)
* Asterisks (*) for bullet points, never dashes
* Regular numbers (1, 2, 3) for ordered lists
* Dates in day-month-year format (e.g., 3rd April 2025)
* Enclose uncertain points in [square brackets]

### Emails
* Plain text in a code block (never Markdown)
* Always include a subject line

### Code discussions
<!--
Adjust based on your experience level:
* "Assume limited experience writing code" OR
* "Assume strong programming background"
-->

## Key Frameworks

<!--
Add any mental models or frameworks you use regularly.

Examples:
* All AI output should be Checked, Edited and Owned by the human
* Benefits of AI span three dimensions: better, quicker, happier work
* "Trust but verify" — always fact-check AI output
-->

## Data Analysis Workflow

<!--
If you work with data, add your methodology patterns here.

Examples:
* Validate assumptions with spot-checks before proceeding
* Document limitations and caveats in reports
* Prefer absolute counts over shares for volume metrics
* Include Source column for data provenance
-->

## Python Environment Strategy

* **Tool packages** (pandas, requests, etc.): Install with `pip3 install --user` — globally available
* **CLI tools** (black, ruff): Use `pipx install` — isolated but global
* **Project venvs**: Only create when the project has specific version requirements

## Cloud Sync Management

<!--
If you use cloud sync (Dropbox, iCloud, etc.), add patterns here.

Key issues to address:
* High-volume small files (.venv, node_modules, .git) cause sync storms
* The `.nosync` suffix excludes files from Dropbox/iCloud sync
-->

## Technical Patterns

* Prefer reusable scripts over one-off operations
* Long-running scripts: implement progress tracking and resume capability
* Pausable projects: README must include status, resume commands, and next steps
* HTTP clients: add per-request timeouts (30s) to prevent hangs

<!--
Add your own learned patterns here as you work.
-->

## Project Contacts

<!--
Track key contacts for ongoing projects.

| Name | Email | Role |
|------|-------|------|
| Example Person | example@company.com | Project lead |
-->

## Notifications

<!--
If you set up notification skills (Telegram, email, etc.), document usage here.

| Method | Best for | Response needed? |
|--------|----------|------------------|
| Email | Reports, detailed results | No |
| Telegram | Questions, decisions needed | Yes |
-->
