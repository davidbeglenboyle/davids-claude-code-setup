# CLAUDE.md Sections Explained

What each section does and why it matters.

## Overview

CLAUDE.md is your personal instruction file for Claude Code. It's loaded automatically at the start of every session, giving Claude context about how you work.

**Location:** `~/.claude/CLAUDE.md`

**Key principle:** This file is *memory*. Anything you'd otherwise repeat across sessions belongs here.

---

## Section-by-Section Guide

### Professional Context

**Purpose:** Gives Claude background on your expertise and domain.

**Why it matters:** Claude tailors explanations based on your background. A data scientist gets different explanations than a marketing manager.

**What to include:**
- Your role and company
- Relevant experience/domains
- Current focus areas

**Example:**
```markdown
## Professional Context
Jane Smith is a Product Manager at TechCorp, working on developer tools.
Background includes software engineering and technical writing.
```

---

### Project Directory Structure

**Purpose:** Tells Claude where you keep things.

**Why it matters:** When you say "work on my project", Claude knows where to look. Eliminates constant "where is that file?" questions.

**Key elements:**
- Primary working folder (where new projects go)
- GitHub repos location
- Naming conventions

**Tip:** The naming convention `YYYY-MM-DD-project-name` keeps folders sorted chronologically.

---

### Documentation Hierarchy

**Purpose:** Establishes precedence when multiple CLAUDE.md files exist.

**Why it matters:** You might have global preferences but project-specific overrides. This section clarifies which wins.

**Standard hierarchy:**
1. User-level (`~/.claude/CLAUDE.md`) — global
2. Project-specific (repo root) — overrides global
3. Sub-project (nested) — overrides parent

---

### Session Context Loading

**Purpose:** Tells Claude what to read at session start.

**Why it matters:** For multi-session work, Claude needs context. This section automates "please read [file] first".

**What to include:**
- Notes/diary location
- Decision patterns document
- Project READMEs

---

### Working Directory Rules

**Purpose:** Establishes file organisation patterns.

**Why it matters:** Without rules, projects become cluttered. These patterns keep things navigable.

**Key rules:**
- Archive policy (move old files, don't delete)
- Folder structure (scripts vs outputs vs summaries)
- Naming conventions for deliverables

---

### Context Engineering

**Purpose:** Patterns for creating useful files.

**Why it matters:** Well-named files with clear first lines reduce cognitive load. Future-you (and Claude) can understand without opening everything.

**Key patterns:**
- Descriptive filenames (`api-errors-traced-to-rate-limits.md` not `notes.md`)
- First-line summaries (no preamble)
- README templates

---

### Communication Preferences

**Purpose:** How you want Claude to write.

**Why it matters:** Everyone has style preferences. This section encodes yours.

**What to include:**
- Tone (formal vs conversational)
- Formatting preferences
- Things to avoid (jargon, excessive hedging, etc.)

**Tip:** Be specific. "Don't use acronyms" is clearer than "be accessible".

---

### Key Frameworks

**Purpose:** Mental models you use regularly.

**Why it matters:** Claude can apply your frameworks consistently. Instead of explaining "my 3-step process" each time, define it once.

**Examples:**
- Decision-making frameworks
- Quality checklists
- Core beliefs about your domain

---

### Data Analysis Workflow

**Purpose:** Methodology patterns for working with data.

**Why it matters:** Data work has many pitfalls. These patterns prevent common mistakes.

**What to include:**
- Validation approaches
- Documentation requirements
- Provenance tracking

**Skip if:** You don't work with data regularly.

---

### Python Environment Strategy

**Purpose:** How to manage Python installations.

**Why it matters:** Virtual environment confusion wastes time. Clear rules prevent "which pip?" problems.

**Standard approach:**
- User installs (`pip3 install --user`) for tools
- `pipx` for CLI tools
- Project venvs only when needed

---

### Cloud Sync Management

**Purpose:** Patterns for Dropbox/iCloud/etc.

**Why it matters:** Sync services + development files = problems. These patterns prevent sync storms.

**Key issues:**
- `.venv`, `node_modules`, `.git` cause problems
- The `.nosync` suffix excludes from sync
- Symlink pattern: `.venv.nosync` + symlink

**Skip if:** You don't use cloud sync for development files.

---

### Technical Patterns

**Purpose:** Accumulated "how to do X" knowledge.

**Why it matters:** You learn things the hard way. Recording them prevents repeating mistakes.

**What to include:**
- Tool-specific patterns (pandoc, ffmpeg, etc.)
- Error handling approaches
- Platform quirks

**Tip:** Add patterns as you discover them. This section grows over time.

---

### Project Contacts

**Purpose:** Key people for ongoing work.

**Why it matters:** When drafting emails or understanding context, Claude can reference who's who.

**What to include:**
- Names and roles
- Email addresses (if helpful)
- Project associations

---

### Notifications

**Purpose:** How Claude should alert you.

**Why it matters:** If you've set up notification skills (Telegram, email), document when to use each.

**Standard pattern:**
| Method | Use case |
|--------|----------|
| Email | Reports, non-urgent results |
| Telegram | Questions needing response |
| iMessage | Quick alerts (macOS only) |

---

## Tips for Maintaining CLAUDE.md

### Start Small
Begin with 3-4 sections. Add more as you discover patterns.

### Be Specific
"Don't use jargon" is better than "be clear". Examples help.

### Update Regularly
When you find yourself correcting Claude repeatedly, add a rule.

### Don't Duplicate
If something belongs in a project CLAUDE.md, don't also put it in global.

### Test Changes
After adding rules, verify Claude follows them in the next session.

---

## Project-Specific CLAUDE.md

Besides the global file, you can create project-specific versions:

**Location:** `project-folder/CLAUDE.md`

**Use for:**
- Project-specific conventions
- Team preferences (if sharing)
- Technology-specific patterns

**Example:**
```markdown
# Project X - Claude Preferences

This project uses React and TypeScript. All components go in src/components/.

Code style: Use functional components with hooks.
Testing: Every component needs a .test.tsx file.
```

These override global settings for that project only.
