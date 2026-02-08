# David's CLAUDE.md Additions

Specific additions to the template that reflect my working style. Adapt or ignore as suits you.

---

## The Economist Style

I prefer writing in The Economist's house style:

* Short sentences, one-idea paragraphs
* Active verbs, precise nouns, understated wit
* Front-load with a striking fact or analogy; end with a forward-looking takeaway
* Spell out numbers below eleven; never open a sentence with a digit
* Analytic, sceptical tone — present evidence, weigh counter-arguments, draw a clear conclusion

This applies to reports, emails, and other prose. Not code comments.

---

## The CEO Principle

All AI output should be **Checked, Edited and Owned** by the human.

This isn't about distrust — it's about accountability. Claude produces drafts; I produce final work.

---

## Data Hoarding Philosophy

When hitting an API:
- Capture as much raw data as possible
- Process and slim down for analytics
- Never throw away data you're already retrieving
- Save raw responses alongside processed outputs — future analysis may need fields you didn't anticipate

Storage is cheap. API calls are expensive.

---

## Archive, Don't Delete

When updating or replacing files (especially Markdown):
- Archive the old version to `/archive` subfolder
- Don't delete unless truly obsolete
- Archive folders can accumulate — that's fine

This creates implicit version history without git for quick projects.

---

## First-Line Discipline

Every markdown file starts with a one-sentence summary. No heading first, no preamble.

```
This project extracts podcast listening patterns from API data.

## Overview
...
```

The first line should answer "what is this?" without reading further.

---

## Descriptive Filenames Over Generic

File names should summarise content:
- **Good:** `api-429-errors-traced-to-rate-limits.md`
- **Bad:** `notes.md`, `analysis.md`, `draft.md`

You should understand what's in a file without opening it.

---

## Sub-Agent Patterns

For complex work with sub-agents:

1. **Write to files, not memory** — Sub-agents should save output to individual files. This makes work resumable and auditable.

2. **Explicit contracts** — When launching sub-agents, specify:
   - Input files/paths
   - Output path and format
   - Success criteria

3. **Verify reports** — Exploration agents may report incorrect details. Always verify with direct tools before acting.

4. **Large files via bash** — Files over 100KB may fail via sub-agents. Use bash directly.

---

## Notification Selection

When Claude should notify me (using notification skills):

| Situation | Method |
|-----------|--------|
| Task complete, no response needed | Email |
| Quick status update | iMessage |
| Question requiring decision | Telegram |
| Error or blocking issue | Telegram |
| Long-running task progress | Email (hourly) |

Batch minor updates; don't notify for every small step.

---

## Open Files Automatically

When creating a file I need to review (reports, documents, emails):
```bash
open [filepath]
```

Don't wait to be asked. If it's something I'll read, open it.

---

## Manifest-Before-Execute

For destructive or batch operations:
1. Generate reviewable manifest (CSV/JSON)
2. Get user approval
3. Execute from manifest

This prevents "oops, that wasn't what I meant" situations.

---

## Long Task Protocols

For tasks taking 1+ hours:
- Send hourly progress updates (counts, percentages, ETAs)
- Save results incrementally (not just at the end)
- Include resume instructions if interrupted

---

## Square Bracket Approval Workflow

For sensitive documents:
1. Mark proposed changes with `[square brackets]`
2. User reviews and approves
3. Remove brackets to finalise

Example:
```
The project will [launch in Q2] with [budget of £50k].
```

This makes changes explicit for review.

---

## README Requirements for Pausable Projects

Every project that might be paused needs:
1. **Status** — Active / Paused / Complete, with date
2. **Current state** — What's done, what's pending
3. **How to resume** — Exact commands or next steps
4. **Key files** — What each important file does

Future-me (or Claude) should be able to pick up without context.

---

## CLAUDE.md Diet: Rules Files

When CLAUDE.md exceeds ~300 lines, extract domain-specific sections into `~/.claude/rules/`:

```
~/.claude/rules/
├── data-analysis.md          # Data workflows, Python env, cloud sync
├── technical-patterns.md     # Accumulated tool knowledge
├── secrets-management.md     # Credential management
└── document-production.md    # Document generation recipes
```

Keep universal preferences (tone, formatting, project structure) in CLAUDE.md. Everything loads automatically — no configuration needed.

**The principle:** CLAUDE.md should contain what applies to *every* session. Rules contain what applies to *some* sessions.

---

## Mechanical Quality Scoring

Run `quality-score` before sharing deliverables. It catches things you'd notice on a second read:

- Unresolved `[square brackets]` from your approval workflow
- TODO/FIXME markers
- Missing first-line summaries in markdown
- Stale generated files (`.docx` older than source `.md`)

No LLM involved — pure regex. Fast, deterministic, incorruptible.

---

## Structured Self-Critique

Use `/devils-advocate` before sending client deliverables. Six lenses:

1. **Audience** — Right framing for who'll actually read it?
2. **Evidence** — What supports the claims? What contradicts them?
3. **Alternative Framing** — Two different ways to present the same insight
4. **Complexity** — Could it be simpler without losing substance?
5. **Action** — What would the reader actually *do*?
6. **Paradox** — Does this contradict your core beliefs?

Every challenge must quote specific text — no generic critiques allowed.
