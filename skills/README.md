# Skills

Custom skills that extend Claude Code's capabilities.

## Directory Structure

| Folder | Contents |
|--------|----------|
| `ready-to-use/` | Copy directly into `~/.claude/skills/` — no setup needed |
| `needs-credentials/` | Require API keys or OAuth setup — see SETUP.md in each |
| `david-specific/` | Skills not included, documented for reference |

## Installation

### Single Skill

```bash
cp -r ready-to-use/chart-design ~/.claude/skills/
```

### All Ready-to-Use Skills

```bash
cp -r ready-to-use/* ~/.claude/skills/
```

## Ready-to-Use Skills (14)

### Design & Visualization

| Skill | Description |
|-------|-------------|
| **chart-design** | Apple HIG-inspired principles for effective data visualization |
| **frontend-design** | Production-grade web UI generation with distinctive aesthetics |
| **threejs-builder** | Three.js web app generation with modern ES modules |

### Document Processing

| Skill | Description |
|-------|-------------|
| **docx** | Markdown-to-Word conversion using branded templates |
| **pdf** | PDF manipulation: extract, merge, split, fill forms |
| **pptx** | PowerPoint creation and editing |
| **pdf-to-markdown** | Full PDF text extraction for context loading |
| **markitdown** | Microsoft's file-to-Markdown converter (PDF, DOCX, images, etc.) |

### Workflow & Productivity

| Skill | Description |
|-------|-------------|
| **plan-with-files** | Manus-style file-based task planning with progress tracking |
| **edit** | Spatial editing with `{curly brace}` markers in Markdown |
| **release-notes** | Changelog generation from git history or manual input |
| **skill-creator** | Meta-skill for creating new skills |

### Development

| Skill | Description |
|-------|-------------|
| **nano-banana-builder** | Next.js + Google Gemini image generation apps |
| **google-official-seo-guide** | Official Google SEO documentation reference |

## Needs-Credentials Skills (5)

Each includes a `SETUP.md` with step-by-step instructions.

| Skill | Service | What You Need |
|-------|---------|---------------|
| **calendar** | Google Calendar | OAuth credentials + token |
| **callme** | Telegram | Bot token from BotFather |
| **sendemail** | Gmail SMTP | App password |
| **scrobble** | Last.fm | API key + session key |
| **gdocs-sync** | Google Docs | OAuth credentials + token |

## From Anthropic (Reference)

These skills come from [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins). Install via Claude Code's plugin marketplace:

```
/plugins install data-analysis
/plugins install sales
/plugins install legal
```

Available plugin suites:
- `data-analysis/*` — SQL, exploration, visualization, dashboards
- `sales/*` — Prospecting, call prep, competitive intelligence
- `marketing/*` — Content creation, campaign planning, SEO
- `finance/*` — Journal entries, reconciliation, statements
- `product-management/*` — Specs, roadmaps, research synthesis
- `enterprise-search/*` — Cross-tool search and digests
- `productivity-anthropic/*` — Task management, memory
- `legal/*` — Contract review, NDAs, compliance

## Creating Your Own Skills

Use the `skill-creator` skill to generate new skills:

```
/skill-creator
```

Or create manually:

1. Create folder in `~/.claude/skills/your-skill-name/`
2. Add `SKILL.md` with frontmatter and instructions
3. Restart Claude Code

See `skill-creator/SKILL.md` for detailed guidance.
