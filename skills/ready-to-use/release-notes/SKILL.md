---
name: release-notes
description: |
  Generate release notes for any project, with or without git.

  Use when: user asks to "create release notes", "write release notes", "generate changelog",
  "document what changed", or runs /release-notes. Also use when user asks to set up
  release notes infrastructure for a project.

  Works in two modes:
  - Git repos: Analyzes commits since last release
  - Non-git projects (e.g., CC-WORK): Uses existing CHANGE-NOTES files, file modification
    times, and conversation context to generate release notes
---

# Release Notes Generator

Generate user-focused release notes from project changes.

## Step 1: Detect Project Type

```bash
# Check if git repo
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo "MODE: git"
else
  echo "MODE: non-git"
fi
```

---

## Git Mode (for GitHub repos)

### Find Last Release

```bash
LAST_RELEASE=$(ls -t release-notes/*.md 2>/dev/null | grep -v README | head -1)
if [ -n "$LAST_RELEASE" ]; then
  SINCE_DATE=$(basename "$LAST_RELEASE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
fi
```

### Get Commits

```bash
if [ -n "$SINCE_DATE" ]; then
  git log --since="$SINCE_DATE" --pretty=format:"%h|%s|%an|%ad" --date=short
else
  git log -50 --pretty=format:"%h|%s|%an|%ad" --date=short
fi
```

### Categorize by Commit Message

| Category | Patterns |
|----------|----------|
| **New Features** | `feat:`, `add:`, `new:`, starts with "Add" |
| **Improvements** | `improve:`, `enhance:`, `update:`, `refactor:` |
| **Bug Fixes** | `fix:`, `bugfix:`, starts with "Fix" |
| **Documentation** | `docs:`, `doc:` |

---

## Non-Git Mode (for CC-WORK projects)

### Step 1: Find Existing Change Documentation

Look for these files in the project:
- `CHANGE-NOTES-*.md` — Session change logs
- `CHANGELOG.md` — Running changelog
- `README.md` — May have "Recent Changes" section

```bash
# Find change documentation
ls -t CHANGE-NOTES-*.md CHANGELOG.md 2>/dev/null | head -5
```

### Step 2: Find Recently Modified Files

```bash
# Files modified in last 7 days (excluding common noise)
find . -type f -mtime -7 \
  ! -path './.git/*' \
  ! -path './archive/*' \
  ! -path './__pycache__/*' \
  ! -name '*.pyc' \
  ! -name '.DS_Store' \
  -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -20
```

### Step 3: Gather Context

1. **Read the most recent CHANGE-NOTES file** — This contains session summaries
2. **Check file modification times** — What's been touched recently
3. **Review the conversation** — What work was discussed in this session
4. **Ask the user** if unclear: "What were the main changes since [last release date]?"

### Step 4: Synthesize Release Notes

Combine information from:
- Existing CHANGE-NOTES files (primary source)
- File modification patterns
- Session context

---

## Output Format

Create file: `release-notes/YYYY-MM-DD-[brief-title].md`

Or for CC-WORK projects without release-notes folder, update: `CHANGE-NOTES-YYYY-MM-DD.md`

```markdown
# Release Notes — [Date in "1st February 2026" format]

## Summary
[2-3 sentence overview of what changed and why it matters to users]

## New Features
- **[Feature name]**: [User-focused description]

## Improvements
- **[Area improved]**: [What got better]

## Bug Fixes
- **[What was fixed]**: [Before vs after]

## Technical Notes
[Optional: Breaking changes, migration steps]

---
*Based on changes since [last release date]*
```

---

## Writing Guidelines

- **Lead with user benefit**: "You can now..." not "Implemented..."
- **Be specific**: "Export crosstabs to CSV" not "Added export"
- **Group related changes**: Multiple file edits for one feature = one bullet
- **Skip internal noise**: Config tweaks, formatting, test-only changes
- **Include breaking changes**: Anything requiring user action

---

## Setup (First Run)

For git repos, create `release-notes/` directory if missing.

For CC-WORK projects, use existing `CHANGE-NOTES-*.md` pattern — no new directory needed.
