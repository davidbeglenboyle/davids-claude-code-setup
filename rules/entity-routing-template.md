Entity routing pattern for multi-client / multi-business work, where one Claude Code setup serves several distinct organisations with different branding, email routing, and project conventions.

## When to use this rule file

Copy this file into `~/.claude/rules/entity-routing.md` (drop the `-template` suffix) if any of the following apply:

* You run two or more distinct businesses, brands, or client engagements from the same laptop
* You need Claude Code to draft emails using different sending addresses depending on context
* Your GitHub repos serve different audiences (some private to a client, some public, some internal-only)
* You've noticed that "which project is this?" and "who's this email for?" decisions slow you down at the start of every session

If you only work on one entity, skip this file — it's overhead you don't need.

## The core idea

Claude Code's working context is set by what directory you're in. If your work for every entity lives in one flat folder, every session starts with "wait, which of these is the big client engagement and which is the side business?". That ambiguity costs you compounding seconds and occasionally costs you a misrouted email.

The fix is to **make directory membership the primary signal for entity routing**, then let a small `project-config.json` confirm the assignment for edge cases. Skills and rules can then ask "which entity is this project under?" without needing a model call.

## Worked example

This template uses four fictional entities throughout so the structural patterns are concrete. Replace them with your real entities when you copy the file.

| Alias | Role | Brand |
|---|---|---|
| **Acme Strategy Group** | Your main consultancy (owned business, commercial work) | Poppins, purple accent |
| **Bridgeport Advisory** | A co-founded boutique (owned, coaching / training delivery) | Source Serif 4 / DM Sans, navy |
| **Harlow & Co** | An external client — a major engagement in a client's org | Arial, client's kelly green |
| **Vertex Forum** | A cross-entity advisory relationship — 10+ years with a conference/media group, spans multiple of the above plus your personal capacity | No brand of its own; uses the hosting org's branding |

Note the four shapes: **two owned businesses, one major external client, one cross-entity advisory relationship**. This is a common senior-consultant setup and worth modelling explicitly — the taxonomy is what stops you from either cramming everything into "clients" or over-splitting into one folder per engagement.

## The acknowledged-blur note

Before describing structure, acknowledge that entities blur. Coaching projects formally owned by Bridgeport often serve Acme clients. Some GitHub repos serve both owned businesses. Vertex Forum spans all three plus you-individually-as-keynote-speaker. **This is known and acceptable.** The goal of routing isn't perfect categorisation — it's making 90% of decisions automatic so the remaining 10% get deliberate human attention.

When you copy this file, write your own blur note. Naming the fuzzy edges up-front keeps them from becoming decision fatigue later.

## Directory structure

All work lives under a single top-level folder (typical: `~/CC-WORK/` or `~/Work/`), organised into entity directories:

```
~/CC-WORK/
├── db-acme/                    # Acme Strategy Group (owned main business)
├── db-bridgeport/              # Bridgeport Advisory (owned boutique)
├── db-harlow/                  # Harlow & Co (major external client)
├── db-vertex/                  # Vertex Forum (cross-entity advisory)
├── db-personal-projects/       # Family, hobbies, non-work
└── db-utilities/               # Claude Code tools, automation, infrastructure
```

The `db-` prefix is a convention: it groups all work directories together when sorted alphabetically and makes them visually distinct from other top-level folders in a sync-tool UI. Any prefix works; consistency matters more than the specific letters.

**Two neutral directories** sit outside the entity split:

* `db-personal-projects/` — family, hobbies, personal experiments. Not routed to any business.
* `db-utilities/` — scripts, tooling, Claude Code config scratchpads. Entity-neutral infrastructure.

## Per-entity layout

Each entity directory has a consistent internal shape: a knowledge base at the root plus dated sub-project folders.

```
db-acme/
├── CLAUDE.md                   # Entity-level overview and working notes
├── direction/                  # KB workstream: strategic direction
├── clients/                    # KB workstream: client list, briefs, history
├── products-and-services/      # KB workstream: your offerings
├── team/                       # KB workstream: who does what
├── 2026-01-15-project-alpha/   # Dated sub-project folders
├── 2026-02-08-project-beta/
├── 2026-03-22-project-gamma/
└── archive/                    # Superseded or closed projects
```

The root-level folders (`direction/`, `clients/`, etc.) hold the evergreen knowledge base — ongoing reference material organised into stable workstreams. Dated folders hold time-bounded projects: proposals, client engagements, one-off analyses. The naming convention `YYYY-MM-DD-project-name/` makes the start date recoverable and keeps `ls` output chronologically ordered.

For the major-client case (`db-harlow/`), a slightly different shape makes sense:

```
db-harlow/
├── CLAUDE.md
├── 1.0-discovery/              # Workstream folders named with numeric prefix
├── 2.1-training-programme/
├── 2.2-adoption-measurement/
├── projects/                   # One subfolder per standalone project within the engagement
│   ├── 2026-03-10-partner-briefings/
│   └── 2026-03-24-dashboard-refresh/
├── fetched/                    # Raw material pulled from the client's Drive/SharePoint
├── general-drive/              # A local mirror of the client's general drive
├── reference/                  # Background reading, earlier deliverables
├── work-generated/             # Draft outputs before they ship to the client
└── archive/
```

The numeric workstream prefixes (`1.0-`, `2.1-`) match how the client organisation itself talks about the phases of work — stealing their vocabulary reduces translation friction in briefings.

For the cross-entity advisory case (`db-vertex/`):

```
db-vertex/
├── CLAUDE.md
├── learning-product/           # Ongoing product workstream
├── cannes-2026/                # Event-specific subfolder
├── october-denver-2026/
├── reference/                  # Historical agendas, retreat materials, past keynotes
└── contacts/                   # People intelligence (who's who in the org)
```

Cross-entity relationships accumulate history over years, so `reference/` and `contacts/` become load-bearing folders in a way they aren't for time-bounded engagements.

## The `project-config.json` schema

Inside any sub-project folder, a `project-config.json` file provides structured metadata that skills can query. This is optional — the parent directory is still the primary signal — but it's useful for projects that need routing heuristics, workstream membership, or per-project processing rules.

```json
{
  "entity": "acme",
  "project_name": "Project Alpha",
  "project_start": "2026-01-15",
  "status": "active",
  "workstreams": ["direction", "clients"],
  "routing": {
    "heuristics": [
      { "match": "from:@clientalpha.example", "assign": "clients" },
      { "match": "subject:invoice", "assign": "finance" }
    ],
    "fallback": "ask_user"
  },
  "processing": {
    "decision_tracking": "actions_table",
    "deliverable_naming": "date-suffix"
  },
  "gdocs": {
    "method": "gdocs_branded",
    "brand": "acme"
  },
  "contacts": [
    { "name": "Alex Example", "email": "alex@clientalpha.example", "role": "sponsor" }
  ]
}
```

**Key fields:**

| Field | Purpose |
|---|---|
| `entity` | One of your entity IDs (must match a `db-<entity>/` directory). Skills use this to pick email send-as alias, document branding, and tone |
| `workstreams` | Empty array `[]` means a flat project. Non-empty means the project has internal structure; skills can route content into named workstreams |
| `routing.heuristics` | Ordered match rules for auto-routing incoming content. First match wins |
| `routing.fallback` | What to do when no heuristic matches. `ask_user` prompts interactively; `tmp/` drops it into the project's scratch folder for later triage |
| `processing.decision_tracking` | Pattern for logging decisions in the project — e.g. `actions_table` (flat table of dated actions), `decisions_table` (architecture-decision-record style), `open_questions` (running list) |
| `gdocs.method` | Which Google Docs pipeline to use for branded deliverables (`gdocs_sync` for plain sync, `gdocs_branded` for brand-formatted output) |
| `contacts` | Project-level people list, separate from the entity-level one. Used for briefings |

Skills should validate this schema on read and surface clear errors rather than silently ignoring unknown fields.

## Email routing

The routing table is the single highest-value piece of this pattern. Getting an email sent from the wrong address to a sensitive client is the kind of mistake that compounds — name one entity in an email meant for another and it takes a half-hour conversation to recover trust.

Build a table that maps entity → send-as alias → script invocation. Example:

| Entity | Default sender | Draft-only? | Script flags |
|---|---|---|---|
| Acme Strategy Group | `you@acme.example` | No (direct send) | `gmail_send.py --sender "Your Name <you@acme.example>"` |
| Bridgeport Advisory | `you@bridgeport.example` | Draft (review before send) | `gmail_send.py --draft --sender "Your Name <you@bridgeport.example>"` |
| Harlow & Co (external client) | `yourname@harlow.example` (client's alias, if you have one) | **Always draft** — never send directly to client domains without review | `gmail_send.py --draft --sender "Your Name <yourname@harlow.example>"` |
| Vertex Forum | `you@vertex.example` or personal, depending on capacity | Draft | `gmail_send.py --draft --sender "Your Name <you@vertex.example>"` |
| Personal | Your personal Gmail | Direct | `gmail_send.py` (default sender) |

**Two rules worth keeping invariant:**

1. **All client-facing mail goes to a draft first.** Never let a skill send directly to an external client domain without human review. The cost of adding `--draft` to every invocation is negligible; the cost of one auto-sent email to the wrong person is not.
2. **Entity membership is inferred from the working directory, confirmed by `project-config.json`.** If you're in `db-harlow/projects/foo/` and `project-config.json` says `"entity": "harlow"`, the email skill picks up the Harlow sender without asking. If the two disagree, the skill should ask rather than guess — directory/config mismatches usually mean something is wrong.

Script location is your choice. A common layout: `~/.claude/gmail/gmail_send.py` holds the email-sending shim, and skills reference it by that absolute path.

## GitHub repos grouped by entity

GitHub repos are a second axis of entity membership. A repo typically belongs to one entity's commercial work, with a small set of "infrastructure" repos that serve all entities.

Example layout:

### Acme Strategy Group (owned main)
* `acme-analytics` — Client-facing dashboard. Public repo
* `acme-knowledge-base` — Internal ops, content library. PRIVATE
* `report-toolkit` — Shared toolkit for Acme deliverables. PRIVATE

### Bridgeport Advisory (owned boutique)
* `bridgeport-website` — The static marketing site
* `bridgeport-portal` — Internal coaching client workspace. PRIVATE
* `coaching-templates` — Reusable frameworks, slides, exercises

### Harlow & Co (major client)
* `harlow-usage-analytics` — Usage analysis of the client's internal tooling. PRIVATE, client-specific

### Infrastructure (entity-neutral)
* `personal-assistant-bridge` — Your Telegram / iMessage / email bridges
* `transcript-archive` — Personal meeting transcript archive. PRIVATE
* `setup-repo` — This repo. Public
* `scratchpad` — Throwaway experiments

**Private by default.** New repos should start private unless there's a deliberate reason to publish. Making a private repo public is a one-line change; discovering that a repo you thought was private has been indexed is a bad day.

**Mark sensitive repos explicitly** in the rule file: `PRIVATE. [Collaborator name] must NOT have access` is worth writing out where the repo has restrictions that aren't obvious from the name. The few seconds to add the note saves you from accidentally adding the wrong person as a collaborator six months later.

## Entity discovery convention

When a skill or an agent needs to know "which entity does the current work belong to?", the resolution order is:

1. **Parent directory.** If the current working directory is somewhere under `db-<entity>/`, that's the answer for 90% of cases.
2. **`project-config.json`.** If the parent directory is ambiguous (e.g. the project sits directly under `~/CC-WORK/` instead of an entity folder), read `project-config.json` and use its `entity` field.
3. **Ask.** If neither is decisive, prompt the user. Do not guess.

This ordering makes the file system the primary source of truth and the JSON file a confirming-override. The alternative — making `project-config.json` primary and inferring directory from it — creates more fragile coupling.

## How to adapt this pattern

Copy this file to `~/.claude/rules/entity-routing.md`, then:

1. **Replace the four fictional entities** with your real ones. Keep the four-role taxonomy if it fits (owned main + owned side + major client + cross-entity advisory); collapse to two or three roles if you don't have a cross-entity relationship.
2. **Replace the email routing table** with your real sender aliases and draft-vs-direct rules. If you don't have domain-specific send-as aliases set up in Gmail yet, that's a prerequisite — your email client supports it; your routing rules just need to name the ones you have.
3. **Write your own acknowledged-blur note** for the fuzzy edges. Name them before they become friction.
4. **Seed the GitHub repos list** with your current repos. This section ages fast — expect to update it every few months as new repos appear and old ones get archived.
5. **Start with `project-config.json` as optional.** Add it to new projects; don't retrofit old ones until a skill you're writing needs the structured metadata.

Once the rule file is in place, skills that route emails, pick document templates, or draft content in your voice can all query it rather than hard-coding entity logic. That's what makes the initial investment pay back — one file, many downstream consumers.

## What NOT to put in this file

* **Real client names that are under NDA.** If you can't say "I work with X" publicly, don't say it in a rule file that might leak via an agent prompt.
* **Real email addresses.** Use placeholders; the routing table works with `you@<entity>.example` just as well as with real addresses, and the real addresses should live in `~/.claude/gmail/` config (which is not a rule file).
* **Credentials or API tokens.** Rule files are docs. Secrets belong in a separate `~/.config/secrets/` or equivalent. See the `secrets-management-template.md` in the same `rules/` folder.
* **Anything that changes weekly.** Rule files should change on the order of months. Dated project folders, current-week contacts, and active deliverables belong in project CLAUDE.md files or working notes — not here.
