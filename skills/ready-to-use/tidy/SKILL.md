---
name: tidy
description: This skill should be used when the user asks to "tidy up", "clean up the project", "organise files", "archive old files", "update the README", "prepare for handoff", or when a project needs documentation and file organisation before switching contexts.
---

# Project Tidy Skill

This skill systematically organises and documents a project directory so that file names are intuitive, old versions are archived, the README is current, and a new agent could resume work without confusion.

## When to Use

Invoke this skill:
* At the end of a working session before switching to another task
* When a project folder has accumulated clutter (drafts, old versions, scratch files)
* Before handing off a project to another agent or human
* When file/folder names no longer reflect their contents
* When the README is stale or missing

## Core Workflow

Execute these phases in order. Each phase produces a brief report before proceeding.

### Phase 1: Audit

Survey the current state before making changes.

1. **List all files and folders** in the project root (non-recursive first)
2. **Identify the project's purpose** from README, CLAUDE.md, or filenames
3. **Note potential issues:**
   * Files with version numbers in names (e.g., `report-v2.md`, `analysis-old.py`)
   * Files with dates that don't match the folder date
   * Generic names (`output.csv`, `test.py`, `draft.md`)
   * Multiple files that appear to be versions of the same thing
   * Empty or near-empty files
   * Files that don't belong (downloads, temp files, `.DS_Store`)
4. **Check for existing archive folder** — note what's already archived
5. **Assess folder structure** — for projects with scripts that produce outputs:
   * Are scripts mixed with their outputs? (should be separated)
   * Are summary/key documents mixed with detailed reports? (should be separated)
   * Would a newcomer know which folder to read first?

Present a summary to the user:
```
## Audit Summary

**Project:** [name/purpose]
**Files found:** [count]
**Potential issues:**
- [list each issue with affected files]

Proceed with tidying? [Yes/No]
```

Wait for confirmation before Phase 2.

### Phase 2: Archive

Move outdated, superseded, or draft files to `/archive`.

**Rules for archiving:**
* **Old versions** — If `report-v3.md` exists, archive `report-v1.md` and `report-v2.md`
* **Dated drafts** — Files with old dates when a newer version exists
* **Superseded outputs** — Old data files replaced by newer runs
* **Working files** — Scratch files, experiments, abandoned approaches

**Do NOT archive:**
* The current/final version of any deliverable
* Configuration files still in use
* Scripts that might be reused
* Reference data or templates

**Archive process:**
1. Create `/archive` if it doesn't exist
2. Move files, preserving original names (the archive folder provides context)
3. Log each move

Report:
```
## Archived Files

Moved [count] files to /archive:
- [filename] — [reason]
```

### Phase 3: Reorganize Structure

For projects with scripts that produce outputs, reorganize into clear subfolders.

**Target structure:**
```
project/
├── README.md          ← Overview and how to run
├── scripts/           ← Code that generates outputs
├── reports/           ← Generated outputs (intermediate)
├── summary/           ← Key findings (read first)
└── archive/           ← Superseded files
```

**When to reorganize:**
* Scripts (.py, .sh) are mixed with their outputs (.md, .csv, .json)
* Summary documents are buried among detailed reports
* A newcomer wouldn't know which file to read first

**Reorganization process:**
1. Propose the new folder structure to user
2. Create subfolders
3. Move files to appropriate locations
4. Update any hardcoded paths in scripts
5. Update internal references (imports, output paths)

**Skip this phase if:**
* Project has fewer than 10 files
* There's already a clear separation
* It's a simple single-purpose project

Report:
```
## Reorganized Structure

Created folders: [list]
Moved [count] files:
- [file] → [destination] — [reason]
Updated paths in: [scripts]
```

### Phase 4: Rename

Fix file and folder names to be intuitive and consistent.

**Naming principles (from CLAUDE.md):**
* Project folders: `YYYY-MM-DD-project-name-hyphenated`
* Files: descriptive, lowercase, hyphenated (e.g., `user-analysis-report.md`)
* Remove version numbers from final files (versions live in archive)
* Dates in filenames only when the date is semantically important (e.g., `2025-01-meeting-notes.md`)

**Check for:**
* Misleading names (contents don't match the name)
* Inconsistent capitalisation
* Underscores where hyphens should be (or vice versa, pick one)
* Abbreviations that aren't obvious
* Generic names that could describe anything

**Rename process:**
1. Propose each rename to the user
2. Wait for confirmation
3. Execute renames
4. Update any internal references (imports, links)

Report:
```
## Renamed Files

- [old name] → [new name] — [reason]
```

### Phase 5: Document

Ensure the project is properly documented for future reference.

**README.md requirements:**

Every project should have a README with:

1. **Title** — Clear project name
2. **Status** — Current state (Active / Paused / Complete)
3. **Purpose** — What this project does/produces (1-2 sentences)
4. **Key files** — List of important files with one-line descriptions
5. **How to resume** — Commands or steps to pick up where work left off
6. **Dependencies** — Any tools, APIs, or data sources required
7. **Outputs** — What this project produces and where outputs go
8. **History** (optional) — Major milestones or decisions

**Update process:**
1. Read existing README (if any)
2. Draft updates based on current project state
3. Present draft to user for review
4. Apply changes

**Also check:**
* CLAUDE.md — Is project-specific guidance still accurate?
* Comments in code — Do they reflect current functionality?
* Any dated references — Do they need updating?

### Phase 6: Verify

Final check that everything is in order.

**Verification checklist:**
- [ ] No version numbers in active filenames
- [ ] No obviously outdated files outside /archive
- [ ] README exists and is current
- [ ] File names describe their contents
- [ ] No empty or near-empty files (except intentional placeholders)
- [ ] No temp files, .DS_Store, or other detritus
- [ ] Project folder name follows convention (if applicable)
- [ ] Scripts separated from outputs (if applicable)
- [ ] Clear "read first" location for newcomers

Present final summary:
```
## Tidy Complete

**Files archived:** [count]
**Files renamed:** [count]
**README:** [Created/Updated/Unchanged]

**Project is ready for:**
- [ ] Continued work
- [ ] Handoff to another agent
- [ ] Long-term storage
```

## Special Considerations

### Multi-session projects

For projects spanning multiple sessions, ensure:
* The README has "How to resume" section
* Any running processes are documented
* Environment setup is recorded (venv activation, API keys needed)

### Data analysis projects

Additional documentation needed:
* Data sources and how to refresh them
* Methodology notes
* Known limitations or caveats

### Code projects

Additional checks:
* Dependencies in requirements.txt or package.json
* Environment variables documented
* Test commands in README

## Additional Resources

### Reference Files

For detailed checklists and examples:
- **`references/checklist.md`** — Comprehensive tidying checklist with examples

## User Interaction

Throughout the process:
* **Ask before destructive actions** — Archiving, renaming, deleting
* **Explain reasoning** — Why each change improves the project
* **Accept user overrides** — The user may have reasons to keep things as they are
* **Be thorough but not pedantic** — Focus on changes that genuinely improve clarity

The goal is a project folder that any agent or human could understand in under two minutes.
