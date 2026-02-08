Rule files extend CLAUDE.md by splitting domain-specific instructions into separate auto-loaded files.

## What Are Rules?

Rules are markdown files in `~/.claude/rules/` that Claude Code loads automatically alongside CLAUDE.md at every session start. They work exactly like CLAUDE.md but let you organise instructions by topic.

## Why Use Rules Instead of One Big CLAUDE.md?

A 500-line CLAUDE.md works, but:
- Every session loads everything, even irrelevant sections
- Editing becomes unwieldy
- Universal rules (tone, formatting) get buried in domain-specific patterns

Rules let you split by concern:
- `~/.claude/CLAUDE.md` — universal preferences (tone, structure, workflows)
- `~/.claude/rules/data-analysis.md` — only relevant when working with data
- `~/.claude/rules/secrets-management.md` — credential patterns
- `~/.claude/rules/document-production.md` — document generation recipes

## How They Load

Claude Code scans `~/.claude/rules/` and loads all `.md` files automatically. No configuration needed — just create the file.

### Conditional Loading (Optional)

Add YAML frontmatter to load rules only when working in matching paths:

```yaml
---
paths:
  - "**/*.py"
  - "**/*.csv"
---
# Data Analysis Patterns
...
```

This rule only loads when you're working with Python or CSV files. Without `paths:`, rules load unconditionally.

**Recommendation:** Start with unconditional loading. Only add path triggers if your context window becomes a concern.

## Template Rule Files

This folder contains starter templates:

| File | Purpose | Lines |
|------|---------|-------|
| `data-analysis-template.md` | Data workflow patterns | ~40 |
| `secrets-management-template.md` | Credential management | ~35 |
| `document-production-template.md` | Document generation recipes | ~15 |
| `technical-patterns-template.md` | Accumulated technical knowledge | ~30 |

## Setup

```bash
# Create the rules directory
mkdir -p ~/.claude/rules

# Copy templates (rename by removing "-template")
cp rules/data-analysis-template.md ~/.claude/rules/data-analysis.md
cp rules/secrets-management-template.md ~/.claude/rules/secrets-management.md
```

Then edit each file to match your tools and workflows.

## Writing Good Rules

1. **Be specific.** "Use pandas for CSV files" is better than "use appropriate tools"
2. **Include context.** "Use `--break-system-packages` on macOS because Homebrew Python blocks system-wide pip"
3. **Accumulate organically.** When Claude makes a mistake, add a rule to prevent recurrence
4. **One topic per file.** Don't create a catch-all rule file — that's just another CLAUDE.md
