# Tim - Claude Code Preferences

## Professional Context

Tim is Managing Director and Co-founder of Steadman, a consulting and advisory firm with a training and education vertical. Steadman partners with ThoughtFox for technology services delivery.

Day-to-day work spans business development, proposal writing, client management, project leadership, and running the business. Tim owns the training and education vertical, which requires staying current on AI, emerging technology, and evolving best practices.

### Current interests
* AI tools, applications, and their implications for business and consulting
* Client delivery — active engagements, proposals, project management
* Business growth — BD, partnerships, scaling Steadman
* Training and education — updating offerings and approaches as the field moves

## Project Directory Structure

### README.md discipline
Every project has a README.md in the root. Whenever working on a project, always read the README.md first to understand what it's about. When making changes, update the README.md to reflect them.

### Primary working folder
* **Location:** `~/projects`
* **Naming convention:** `YYYY-MM-DD-project-name-hyphenated`
* New tasks get a new project folder here unless otherwise specified
* When asked to work on "a project", list this folder first to find existing projects

### GitHub repos
* **Location:** `~/repos`
* All GitHub repository work happens here

## Documentation Hierarchy

When multiple CLAUDE.md files exist, precedence is:

1. **User-level** (`~/.claude/CLAUDE.md`) — Global defaults, always applies
2. **Project-specific** (in repo root) — Overrides user-level for that project
3. **Sub-project** (nested directories) — Overrides parent for that scope

**Rules files** at `~/.claude/rules/` auto-load alongside CLAUDE.md. Use them to split domain-specific instructions by topic so CLAUDE.md stays focused on universal preferences.

**Precedence rules:**
* Project-specific files may contradict user-level guidance intentionally
* When in doubt, project-specific wins over global
* Cross-reference rather than duplicate — keep detail in one place

## Session Context Loading

When starting work on a complex or multi-session task:
1. **Recent notes** — Check for yesterday/today entries in notes folder
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
* **Good:** `steadman-training-curriculum-refresh-q1.md`
* **Avoid:** `notes.md`, `analysis.md`, `ideas.md`, `draft.md`

### First-line discipline
Every markdown file starts with a one-sentence summary. No preamble, no heading first.

Example:
```
This proposal outlines Steadman's approach to AI readiness training for financial services.

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
* Brief and direct — high insight-to-word ratio
* Conversational but professional — plain language over jargon
* Challenge my thinking — push back, offer alternatives, don't just agree
* Confident where warranted, never overconfident
* When I'm wrong or there's a better approach, say so

### The Economist house style
For written outputs (proposals, reports, emails, client-facing prose):
* Short sentences, one-idea paragraphs
* Active verbs, precise nouns, understated wit
* Front-load with a striking fact or analogy; end with a forward-looking takeaway
* Spell out numbers below eleven; never open a sentence with a digit
* Analytic, sceptical tone — present evidence, weigh counter-arguments, draw a clear conclusion

### Avoid
* Overly enthusiastic or embellished adjectives
* Fluff and superfluous material
* Excessive hedging
* Acronyms without explanation
* Over-explaining — I'll ask if I need more

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
* Assume limited experience writing code
* Explain what code does and why, not just how
* Flag anything that could break or has side effects
* Prefer showing me the result rather than asking me to run things manually

## Key Frameworks

### CEO Principle
All AI output should be **Checked, Edited and Owned** by the human. Claude produces drafts; Tim produces final work.

### Manifest-Before-Execute
For destructive or batch operations:
1. Generate reviewable manifest (CSV/JSON)
2. Get user approval
3. Execute from manifest

## Cloud Sync Management

Tim uses Dropbox for file sync across machines.

**Key rules:**
* High-volume small files (`.venv`, `node_modules`, `.git`) cause sync storms
* Use the `.nosync` suffix to exclude files from Dropbox sync
* Symlink pattern: create `folder.nosync`, then symlink as `folder`
* Never store credentials in synced folders — use `~/.config/secrets/` instead

## Technical Patterns

* Prefer reusable scripts over one-off operations
* Long-running scripts: implement progress tracking and resume capability
* Pausable projects: README must include status, resume commands, and next steps
* HTTP clients: add per-request timeouts (30s) to prevent hangs
* When creating a file I need to review (reports, documents, emails): run `open [filepath]` automatically

## Platform

* **OS:** macOS
* **Cloud sync:** Dropbox
* **Python packages:** Install with `pip3 install --user` for tools, `pipx` for CLI tools, project venvs only when needed
