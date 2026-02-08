# David's Claude Code Setup

A shareable collection of Claude Code configurations, skills, and workflows developed by David Boyle at Audience Strategies.

## What's Here

This repository contains sanitized versions of my Claude Code setup that you can adapt for your own use:

| Folder | Contents |
|--------|----------|
| `claude-md/` | CLAUDE.md templates and section explanations |
| `skills/ready-to-use/` | Skills you can copy directly (no credentials needed) |
| `skills/needs-credentials/` | Skills requiring API keys, with setup guides |
| `skills/david-specific/` | Documentation of skills not included (and why) |
| `settings/` | Permission templates, configuration guides, and safety patterns |
| `bin/` | Helper scripts (sanitized) |
| `mcp-servers/` | MCP server setup instructions |

## Quick Start

1. **New to Claude Code?** Start with `SETUP-GUIDE.md`
2. **Multi-machine setup?** Read `STORAGE-OPTIONS.md` for sync strategies
3. **Want skills?** Browse `skills/ready-to-use/` and copy what you need
4. **Customising CLAUDE.md?** See `claude-md/SECTIONS-EXPLAINED.md`

## Philosophy

**Skills reference paths, not credentials.** Every skill that needs authentication points to a standard location (`~/.config/secrets/`) rather than embedding credentials. This keeps your setup shareable and secure.

**Placeholder sections over deletions.** The CLAUDE.md template includes empty placeholder sections for personal context, contacts, etc. — add your own rather than starting from scratch.

**Storage-agnostic.** While I use Dropbox for multi-machine sync, these patterns work with iCloud, OneDrive, Syncthing, or local-only setups.

## Skills Overview

### Ready to Use (14 skills)

Copy directly into `~/.claude/skills/`:

* **chart-design** — Apple HIG-inspired data visualization principles
* **frontend-design** — Production-grade web UI generation
* **plan-with-files** — Manus-style file-based task planning
* **edit** — Spatial editing with {curly brace} markers
* **release-notes** — Changelog generation from git or manual input
* **skill-creator** — Meta-skill for creating new skills
* **threejs-builder** — Three.js web app generation
* **nano-banana-builder** — Next.js + Google Gemini image apps
* **google-official-seo-guide** — Official Google SEO documentation
* **markitdown** — Microsoft's file-to-Markdown converter
* **pdf** — PDF manipulation toolkit
* **docx** — Markdown-to-Word conversion
* **pptx** — PowerPoint creation and editing
* **pdf-to-markdown** — Full PDF text extraction

### Needs Credentials (5 skills)

Each includes a `SETUP.md` with human and AI agent setup instructions:

* **calendar** — Google Calendar integration (flights, travel blocks)
* **callme** — Telegram notifications and conversations
* **sendemail** — Gmail SMTP email sending
* **scrobble** — Last.fm music scrobbling
* **gdocs-sync** — Markdown to Google Docs sync

### From Anthropic (Reference Only)

These come from [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — install via Claude Code's plugin marketplace rather than copying:

* `data-analysis/*`, `sales/*`, `marketing/*`, `finance/*`
* `product-management/*`, `enterprise-search/*`, `productivity-anthropic/*`, `legal/*`

## Credential Storage Pattern

I recommend the **synced secrets directory** pattern:

```
~/.config/secrets/              # Standard location (symlink to sync folder)
├── anthropic-api-key           # Plain text, just the key
├── telegram-bot-token
├── gmail-app-password
└── google-calendar/
    ├── credentials.json
    └── token.json
```

Skills then reference paths:
```markdown
## Credentials
Reads token from `~/.config/secrets/telegram-bot-token`
```

See `STORAGE-OPTIONS.md` for multi-machine sync strategies.

## Safety

**[Use `trash` instead of `rm`](settings/SAFETY-TRASH-OVER-RM.md)** — By default, `Bash(rm:*)` in your allow list lets Claude Code permanently delete files without asking. Replace with `Bash(trash:*)` and deny `rm` entirely. Files go to macOS Trash (recoverable) instead of being destroyed.

## About

Created by David Boyle, Director of [Audience Strategies](https://audiencestrategies.com).

This is a personal setup shared with collaborators. Not affiliated with Anthropic (beyond being a happy Claude Code user).

## Status

**Active** — Last updated: 8th February 2026
