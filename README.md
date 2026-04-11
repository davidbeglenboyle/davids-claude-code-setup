# David's Claude Code Setup

A shareable collection of Claude Code configurations, skills, and workflows developed by David Boyle at Audience Strategies.

## What's Here

This repository contains sanitized versions of my Claude Code setup that you can adapt for your own use:

| Folder | Contents |
|--------|----------|
| `claude-md/` | CLAUDE.md templates and section explanations |
| `rules/` | Rule file templates for splitting CLAUDE.md by topic |
| `skills/ready-to-use/` | Skills you can copy directly (no credentials needed) |
| `skills/needs-credentials/` | Skills requiring API keys, with setup guides |
| `skills/david-specific/` | Documentation of skills not included (and why) |
| `agents/` | Agent definitions for critic-fixer pattern (sub-agents) |
| `settings/` | Permission templates, configuration guides, and safety patterns |
| `bin/` | Helper scripts (quality-score, sendemail template) |
| `mcp-servers/` | MCP server setup instructions |

## Quick Start

1. **New to Claude Code?** Start with `SETUP-GUIDE.md`
2. **CLAUDE.md getting long?** See `rules/README.md` to split it into topic files
3. **Multi-machine setup?** Read `STORAGE-OPTIONS.md` for sync strategies
4. **Want skills?** Browse `skills/ready-to-use/` and copy what you need
5. **Want quality review agents?** See `agents/README.md` for the critic-fixer pattern
6. **Customising CLAUDE.md?** See `claude-md/SECTIONS-EXPLAINED.md`
7. **Running bridges, scheduled tasks, or always-on services?** See `SERVICES-GUIDE.md` for LaunchAgents, the services registry pattern, and the TCC Full Disk Access gotchas that will eat your afternoon if you don't know them
8. **Juggling multiple clients or businesses?** See `rules/entity-routing-template.md` for the `db-<entity>/` directory convention, `project-config.json` schema, and email send-as routing table

## Philosophy

**Skills reference paths, not credentials.** Every skill that needs authentication points to a standard location (`~/.config/secrets/`) rather than embedding credentials. This keeps your setup shareable and secure.

**Placeholder sections over deletions.** The CLAUDE.md template includes empty placeholder sections for personal context, contacts, etc. — add your own rather than starting from scratch.

**Storage-agnostic.** While I use Dropbox for multi-machine sync, these patterns work with iCloud, OneDrive, Syncthing, or local-only setups.

## Skills Overview

### Ready to Use (16 skills)

Copy directly into `~/.claude/skills/`:

* **review-loop** — Quality verification cycle: score, critique, fix, re-score (max 3 rounds)
* **devils-advocate** — Structured critique with 5-7 challenges across six categories
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

### Needs Credentials (7 skills)

Each includes a `SETUP.md` with human and AI agent setup instructions:

* **calendar** — Google Calendar integration (flights, travel blocks)
* **callme** — Telegram notifications and conversations
* **sendemail** — Gmail SMTP email sending
* **scrobble** — Last.fm music scrobbling
* **gdocs-sync** — Plain Markdown to Google Docs sync (stable URL)
* **gdocs-branded** — Branded Google Docs from Markdown (fonts, colours, tables, stable URL)
* **linkedin-posts** — Fetch posts and comments via LinkedIn Voyager API using Chrome cookies (no API key, no OAuth)

### From Anthropic (Reference Only)

These come from [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — install via Claude Code's plugin marketplace rather than copying:

* `data-analysis/*`, `sales/*`, `marketing/*`, `finance/*`
* `product-management/*`, `enterprise-search/*`, `productivity-anthropic/*`, `legal/*`

## Rules: Splitting CLAUDE.md by Topic

As CLAUDE.md grows (300+ lines is common), split domain-specific instructions into separate files at `~/.claude/rules/`:

```
~/.claude/rules/
├── data-analysis.md          # Data workflow patterns
├── secrets-management.md     # Credential management
├── document-production.md    # Document generation recipes
├── technical-patterns.md     # Accumulated technical knowledge
└── entity-routing.md         # Multi-client/entity directory + email routing
```

Claude Code loads all rule files automatically alongside CLAUDE.md. See `rules/README.md` for templates and setup.

## Agents: The Critic-Fixer Pattern

The `agents/` folder contains sub-agent definitions used by the `/review-loop` skill:

* **deliverable-critic** — Read-only auditor that checks deliverables against organisation standards. Produces findings with severity levels (HARD FAIL / SHOULD FIX / SUGGESTION)
* **deliverable-fixer** — Edit-capable agent that implements the critic's findings in priority order

The key principle is **separation of powers**: the critic cannot edit, the fixer cannot invent new issues. See `agents/README.md` for setup and customisation.

## Quality Scoring

`quality-score` is a mechanical (no LLM) pre-flight check for deliverables. Starts at 100, deducts for common issues:

```bash
quality-score README.md                    # Score a file
quality-score ~/projects/my-project/       # Score a directory
quality-score report.md --verbose --json   # Detailed JSON output
```

Checks: unresolved `[brackets]`, TODO/FIXME, missing first-line summary, wrong naming convention, stale generated files. Extensible with brand rubrics for client-specific colour and font checks.

See `bin/quality-score` for the script and `bin/README.md` for setup.

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

**Active** — Last updated: 11th April 2026

## Changelog

### 11th April 2026 (gdocs-branded skill)

* Added `gdocs-branded` skill (needs-credentials) — generate branded Google Docs from Markdown with full typography, tables, and stable URLs. Copies a brand-specific Google Docs template, clears the body, and re-populates it with brand-correct fonts, heading colours, and table styling. Three built-in example brands (`editorial`, `corporate`, `modern`) demonstrate different typographic strategies; users can override via `~/.config/google-docs/brands.json`. Requires Google OAuth with Docs + Drive scopes (drive scope needed to copy templates).
* Fixed latent bug in `skills/README.md`: `linkedin-posts` was added on 11th April but the per-folder README still listed 5 needs-credentials skills. Bumped to 7 and added both missing rows.
* This PR supersedes the long-open PR #4 (same feature, branched pre-February Phase 1a, stuck with merge conflicts). Soft-leakage in the original PR's `DEFAULT_BRANDS` dict — three brands whose colour + font combinations fingerprinted real client brands — has been replaced with genuinely generic palettes.

### 11th April 2026 (Phase 1a: operating-system layer)

Two new documentation files that reframe the repo around the patterns that have accumulated since February — bridges, services, scheduled tasks, and multi-entity routing — rather than just skills.

* Added `SERVICES-GUIDE.md` — a top-level guide to running Claude Code as a small operating system: always-on bridges as LaunchAgents, scheduled tasks via Claude Code Desktop, the services registry pattern (`~/.claude/services/registry.json`), the `launchctl bootstrap`/`bootout` modern API, reverse-DNS label namespacing, source ↔ runtime split, install-manifest pattern for clean uninstall, and a detailed TCC Full Disk Access section covering the interactive-vs-headless identity split and the Homebrew Cellar path invalidation gotcha.
* Added `rules/entity-routing-template.md` — a template for multi-client / multi-business work. Uses four fictional entities (Acme Strategy Group, Bridgeport Advisory, Harlow & Co, Vertex Forum) to illustrate the `db-<entity>/` directory convention, per-entity KB + dated sub-projects layout, `project-config.json` schema with routing heuristics, email send-as alias routing table with "all client mail to draft first" invariant, and the parent-directory → config → ask resolution order.

### 11th April 2026 (linkedin-posts)
* Added `linkedin-posts` skill (needs-credentials) — fetch LinkedIn posts and comments for a single person or a configured list. Uses Chrome session cookies via `browser_cookie3` rather than an API key, so setup is "pip install + be signed into LinkedIn in Chrome". Includes a shared `linkedin_posts_lib.py` with silent-reshare detection, GraphQL comments-on-others support, and a `comments-probe.passe` script for re-capturing query IDs when LinkedIn rotates them.

### 8th February 2026 (Phase 2)
* Added `agents/` — deliverable-critic and deliverable-fixer agent definitions
* Added `review-loop` skill — quality verification cycle with critic-fixer pattern
* 16 ready-to-use skills total

### 8th February 2026 (Phase 1)
* Added `rules/` — template rule files for splitting CLAUDE.md by topic
* Added `devils-advocate` skill — structured 6-category critique
* Added `quality-score` script — mechanical pre-flight checker for deliverables
* Updated CLAUDE-TEMPLATE, SETUP-GUIDE, and STORAGE-OPTIONS to cover rules
* Made repository public
