Agent definitions for use with Claude Code's Task tool (sub-agents).

## What Are Agents?

Agents are markdown files that define specialised roles for Claude Code sub-agents. When you launch a sub-agent via the Task tool, you include the agent file's content in the prompt to give the sub-agent its instructions, constraints, and personality.

Unlike skills (which are invoked directly), agents are launched programmatically by other skills or by you.

## How They Work

```
You (or a skill) → Task tool → sub-agent reads agent .md → does the work → returns results
```

The agent file defines:
- **Role** — What the agent does
- **Tools** — Which tools it can use (enforced by the caller, not the file itself)
- **Standards** — What it checks against
- **Output format** — How it reports results

## Included Agents

| Agent | Role | Tools | Used By |
|-------|------|-------|---------|
| **deliverable-critic** | Read-only quality auditor | Read, Grep, Glob | `/review-loop` skill |
| **deliverable-fixer** | Implements critic findings | Read, Edit, Write, Grep, Glob | `/review-loop` skill |

### The Critic-Fixer Pattern

The two agents implement **separation of powers**:

1. The **critic** can only read — it produces findings but cannot change files
2. The **fixer** can only fix what the critic identified — it cannot make additional changes
3. The **review-loop skill** orchestrates the cycle and controls when each runs

This prevents either agent from going rogue. The critic cannot silently fix things; the fixer cannot invent new problems to solve.

## Customisation

Both agents contain `<!-- CUSTOMISE -->` sections where you add your own organisation standards:

1. **deliverable-critic.md** — Add your clients' brand standards (fonts, colours, tone rules, banned words, hard fail criteria)
2. **deliverable-fixer.md** — Add organisation-specific correction patterns (spelling preferences, formatting rules)

## Setup

```bash
# Copy to your agents directory
cp agents/*.md ~/.claude/agents/
```

Claude Code loads agent files from `~/.claude/agents/` — they're available to reference in Task tool prompts.

## Creating Your Own Agents

Follow the pattern:

1. Define the role in one sentence (first line of the file)
2. List allowed tools explicitly
3. Specify the output format
4. Add constraints (what the agent must NOT do)
5. Save as `~/.claude/agents/agent-name.md`

Good agents are **narrowly scoped** — they do one thing well rather than trying to be general-purpose.
