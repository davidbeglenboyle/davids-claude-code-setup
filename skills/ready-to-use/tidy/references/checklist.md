# Comprehensive Tidying Checklist

This reference provides detailed guidance for each phase of project tidying.

## Audit Phase Checklist

### Files to Flag for Review

**Version indicators in filenames:**
* `-v1`, `-v2`, `-final`, `-final-final`
* `-old`, `-new`, `-backup`, `-copy`
* `-draft`, `-wip`, `-temp`
* Dates in filenames that don't match folder date

**Generic or ambiguous names:**
* `output.csv`, `results.json`, `data.xlsx`
* `test.py`, `script.py`, `main.py` (without context)
* `notes.md`, `draft.md`, `ideas.txt`
* `Untitled`, `New Document`, `Copy of...`

**System/temp files to remove:**
* `.DS_Store`, `Thumbs.db`
* `*.pyc`, `__pycache__/`
* `*.log` (unless intentionally kept)
* `*.tmp`, `*.bak`, `*.swp`
* `node_modules/` (should be in .gitignore, not committed)

**Potential duplicates:**
* Files with similar names in different locations
* Files with identical sizes (quick duplicate check)
* Screenshot files (often redundant)

### Questions to Answer During Audit

1. What is this project's primary deliverable?
2. Which files contribute to that deliverable?
3. Which files are intermediate/working files?
4. What's the chronological order of file creation?
5. Are there any files that seem completely unrelated?

## Archive Phase Checklist

### What to Archive

| File Type | Archive If... |
|-----------|---------------|
| Versioned files | Older versions exist (keep only latest) |
| Dated outputs | Newer outputs exist for same purpose |
| Draft documents | Final version has been created |
| Exploration code | Approach was abandoned or superseded |
| Reference materials | No longer actively consulted |
| Meeting notes | Decisions have been documented elsewhere |
| Screenshots | Purpose has been served |

### What NOT to Archive

| File Type | Keep If... |
|-----------|------------|
| Configuration | Still in use (even if old) |
| Templates | May be reused in future |
| Scripts/utilities | Could be needed again |
| Raw data | May need to regenerate outputs |
| Documentation | Still accurate and useful |

### Archive Folder Structure

For simple projects:
```
project/
├── archive/
│   ├── report-v1.md
│   ├── report-v2.md
│   └── old-analysis.py
├── report.md (final)
└── README.md
```

For complex projects with many archived files:
```
project/
├── archive/
│   ├── 2025-01-drafts/
│   │   ├── report-v1.md
│   │   └── report-v2.md
│   └── 2025-01-exploration/
│       ├── approach-a.py
│       └── approach-b.py
├── report.md
└── README.md
```

## Rename Phase Checklist

### Naming Convention Examples

**Good names:**
* `user-segmentation-analysis.py` — describes what it does
* `q4-2024-revenue-report.md` — date is semantically important
* `spotify-api-client.py` — describes the tool's purpose
* `interview-responses-cleaned.csv` — describes content and state

**Bad names:**
* `analysis.py` — too generic
* `report-v3-final-FINAL.md` — version chaos
* `data.csv` — could be anything
* `test2.py` — meaningless

### File Naming Principles

1. **Be specific** — Name should tell you what's inside without opening
2. **Use lowercase** — Avoids case-sensitivity issues
3. **Use hyphens** — More readable than underscores, URL-safe
4. **Front-load meaning** — Important words first
5. **Include type context** — `api-client`, `data-loader`, `report`

### Folder Naming Principles

1. **Use YYYY-MM-DD prefix** for dated projects
2. **Use descriptive suffixes** — `2025-01-15-user-research-spotify`
3. **Avoid abbreviations** — Unless universally understood
4. **Match the project's identity** — What would you call it in conversation?

## Document Phase Checklist

### README Template

```markdown
# [Project Name]

**Status:** [Active / Paused / Complete]

## Purpose

[1-2 sentences describing what this project does]

## Key Files

| File | Description |
|------|-------------|
| `file.py` | [one-line description] |
| `output.csv` | [one-line description] |

## How to Resume

[Commands or steps to pick up where work left off]

```bash
# Example
source .venv/bin/activate
python main.py --continue
```

## Dependencies

- Python 3.11+
- [list other requirements]

## Outputs

[What this project produces and where it goes]

## Notes

[Any important context, decisions, or caveats]
```

### README Quality Checks

- [ ] Could someone understand the project in under 2 minutes?
- [ ] Are the key files listed and described?
- [ ] Is the current status clear?
- [ ] Could someone resume work without asking questions?
- [ ] Are dependencies documented?
- [ ] Are outputs described?

### When to Update CLAUDE.md

Update project-specific CLAUDE.md if:
* The project's purpose or scope has changed
* New conventions have been established
* Dependencies have been added or removed
* The workflow has evolved

## Verify Phase Checklist

### Final Sweep

**File hygiene:**
- [ ] No version numbers in active filenames
- [ ] No `-old`, `-backup`, `-copy` files outside archive
- [ ] No empty files (0 bytes) unless intentional
- [ ] No duplicate content across files
- [ ] No temp/cache files

**Naming consistency:**
- [ ] All files use consistent case (lowercase preferred)
- [ ] All files use consistent separators (hyphens preferred)
- [ ] Names are descriptive and unambiguous
- [ ] Folder name matches YYYY-MM-DD convention if applicable

**Documentation completeness:**
- [ ] README exists and is current
- [ ] Key files are described
- [ ] Resume instructions are provided
- [ ] Dependencies are listed

**Structure clarity:**
- [ ] Active files are in root or clearly named folders
- [ ] Archived files are in /archive
- [ ] No deeply nested unnecessary folders
- [ ] Related files are grouped logically

## Common Patterns and Solutions

### Pattern: Multiple dated versions

**Before:**
```
report-2025-01-10.md
report-2025-01-12.md
report-2025-01-14.md
report-2025-01-15-final.md
```

**After:**
```
report.md                    # current version
archive/
  report-2025-01-10.md
  report-2025-01-12.md
  report-2025-01-14.md
```

### Pattern: Exploration and final

**Before:**
```
analysis-attempt1.py
analysis-attempt2.py
analysis-v3-works.py
analysis-final.py
```

**After:**
```
analysis.py                  # the working version
archive/
  analysis-attempt1.py
  analysis-attempt2.py
  analysis-v3-works.py
```

### Pattern: Mixed content types

**Before:**
```
data.csv
data-cleaned.csv
script.py
output.png
notes.md
```

**After:**
```
spotify-user-data.csv
spotify-user-data-cleaned.csv
data-cleaning-script.py
user-distribution-chart.png
analysis-notes.md
```

### Pattern: Abandoned approach

**Before:**
```
main.py
main-old.py
main-new.py
utils.py
utils-backup.py
```

**After:**
```
main.py                      # current working code
utils.py                     # current utilities
archive/
  main-old.py
  main-new.py               # if superseded
  utils-backup.py
```

## Edge Cases

### When NOT to tidy

* **Active experimentation** — Don't archive approaches still being compared
* **Version control in use** — Git history may be sufficient; archive only if needed for clarity
* **Shared folders** — Coordinate with collaborators before reorganising
* **Compliance requirements** — Some industries require preserving original filenames

### When to ask the user

* Any file you're unsure about archiving
* Files that look important but have confusing names
* Large folders that would take significant time to reorganise
* Anything that might affect running processes or scripts
