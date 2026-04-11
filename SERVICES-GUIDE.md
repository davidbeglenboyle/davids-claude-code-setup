Services, bridges, and scheduled tasks: how to run Claude Code as a small operating system on your laptop, with always-on processes, scheduled jobs, and a unified registry that tracks them.

## When to read this

Read this guide if you've ever thought any of the following:

* "I want Claude to watch my email overnight and draft replies before I wake up"
* "I want to message my own assistant from Telegram / iMessage / Slack while I'm out"
* "I want to run a scheduled agent that pulls a dashboard, analyses it, and pings me if something's off"
* "I've got six background services running and no idea which is alive, which is broken, and which I forgot to remove"

Claude Code's skill system handles on-demand invocations. This guide is about the *other* category: processes that run continuously (bridges), processes that run on a schedule (nightly email triage, weekly digests), and the registry that keeps track of all of them.

Everything here is macOS-specific. Linux and Windows have equivalent mechanisms (systemd user units, Windows Task Scheduler) but the gotchas are different and the scripts in `bin/` target launchd.

## I. What "services" means in this context

Three distinct service types sit under the same umbrella:

| Type | Lifecycle | macOS mechanism | Example |
|---|---|---|---|
| **Always-on bridges** | Run continuously, restart on crash | LaunchAgent with `KeepAlive` | Telegram bridge (polls Bot API, forwards to Claude) |
| **Scheduled tasks** | Fire on a clock, exit when done | LaunchAgent with `StartCalendarInterval` OR a Claude Code Desktop scheduled task | Nightly email triage, weekly digest |
| **On-demand helpers** | Run only when invoked | A script in `~/bin/` | `secret get OPENAI_API_KEY`, `dbx-materialize --git .` |

The first two are the services this guide documents. On-demand helpers are covered in `bin/README.md`.

**Bridges** are the interesting case. A bridge is a long-running process that listens for messages from an external channel (a messaging app, an email account, a webhook endpoint) and routes them into a Claude Code session. The bridge itself is small — a hundred lines of Python — but its value is outsized: it turns Claude from "something you sit at a keyboard to use" into "something you can message from the train and get a draft back by the time you arrive".

**Scheduled tasks** are what Claude Code Desktop's scheduled-task feature (and, as a fallback, direct LaunchAgents) enable. You write a SKILL.md, pick a time, and let Claude execute it unattended. The output usually ends up in a project folder or as a draft email.

## II. The services registry pattern

Once you have two services, you want a registry. Once you have five, you *need* one. The pattern:

**`~/.claude/services/registry.json`** — a single JSON file, synced across machines, listing every service you run. Example:

```json
{
  "services": [
    {
      "id": "telegram-bridge",
      "type": "always-on",
      "label": "io.github.example.setup-repo.telegram-bridge",
      "runtime": "~/.telegram-bridge/",
      "source": "~/CC-WORK/db-utilities/telegram-bridge/",
      "sync_rule": "rsync --exclude '.env'"
    },
    {
      "id": "email-nightly",
      "type": "scheduled-task",
      "label": "(managed by Claude Code Desktop)",
      "skill_path": "~/.claude/scheduled-tasks/email-nightly/",
      "schedule": "04:30 UTC daily",
      "runtime": "~/.email-nightly/"
    },
    {
      "id": "chrome-debug",
      "type": "login-item",
      "label": "chrome-debug-startup",
      "runtime": "~/bin/chrome-debug"
    }
  ]
}
```

The registry is the source of truth: the `services` CLI reads it, the Telegram `/services` command reads it, the multi-machine sync rules come from it.

**What each field does:**

| Field | Purpose |
|---|---|
| `id` | Short human name. Used in CLI commands (`services restart telegram-bridge`) |
| `type` | `always-on`, `scheduled-task`, or `login-item`. Dictates what lifecycle the service follows |
| `label` | The macOS LaunchAgent label, in reverse-DNS form. For Claude Code Desktop scheduled tasks, use a placeholder (`"(managed by Claude Code Desktop)"`) because the label is opaque |
| `runtime` | The stable on-disk location where the service actually runs. **Not** inside `~/Library/CloudStorage/` — see §VI |
| `source` | The synced source location if the service has code (usually inside your work folder). The `services sync <id>` command rsyncs source → runtime |
| `sync_rule` | Any exclusions or flags for the rsync. Typically `--exclude '.env'` so machine-local secrets don't travel |
| `skill_path` | For Claude Code Desktop scheduled tasks, the SKILL.md location under `~/.claude/scheduled-tasks/` |
| `schedule` | Human-readable schedule for scheduled tasks. The real schedule lives in Claude Code Desktop's config file, but recording it here makes the registry browsable |

The registry can grow arbitrarily; prune aggressively. Retired services leave stray plists and runtime directories if you let them.

## III. Always-on bridges as LaunchAgents

Bridges need to survive reboots, restart on crash, and run without an open terminal. That's exactly what LaunchAgents do.

### Label namespace

Use reverse-DNS with your GitHub owner as the root. Example: `io.github.<owner>.<repo>.<component>`. For a setup repo at `github.com/alice/claude-code-setup`, the Telegram bridge label becomes:

```
io.github.alice.claude-code-setup.telegram-bridge
```

This is the 2024-2026 best practice for public distribution — it's unique across the ecosystem and won't collide with any other tool the user installs. **Do not** append version numbers to the label (`...telegram-bridge.v2`); put version metadata *inside* the plist instead so upgrades can `bootout` the old service cleanly.

### Minimum plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>io.github.alice.claude-code-setup.telegram-bridge</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/alice/.telegram-bridge/run.sh</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/Users/alice/.telegram-bridge/logs/stdout.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/alice/.telegram-bridge/logs/stderr.log</string>
</dict>
</plist>
```

**Three gotchas worth calling out:**

1. **`ProgramArguments` must be an array**, even for a single executable. A single-string value fails `launchctl bootstrap` with a cryptic "Input/output error". This is a well-documented trap ([Homebrew discussion #1372](https://github.com/orgs/Homebrew/discussions/1372)).
2. **Absolute paths everywhere.** launchd does not expand `~`, `$HOME`, or any environment variables in plist keys. Write `/Users/alice/...` in full. Your installer script should substitute the real home directory at install time.
3. **Never execute binaries from `~/Library/CloudStorage/`.** macOS blocks this — launchd refuses to run anything inside a File Provider path. Your runtime directory must be outside sync: `~/.telegram-bridge/`, not `~/Dropbox/telegram-bridge/`.

### Load and unload the modern way

The old `launchctl load -w` / `launchctl unload -w` commands are deprecated. They silently fail after repeated cycles and are the single biggest source of "my service used to work" bug reports. Use the newer `bootstrap` / `bootout` API instead:

```bash
# Load
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/io.github.alice.claude-code-setup.telegram-bridge.plist

# Unload
launchctl bootout gui/$(id -u)/io.github.alice.claude-code-setup.telegram-bridge

# Check status
launchctl print gui/$(id -u)/io.github.alice.claude-code-setup.telegram-bridge
```

Homebrew switched to `bootstrap`/`bootout` in [homebrew-services PR #112](https://github.com/Homebrew/homebrew-services/pull/112); every new LaunchAgent tool should follow suit.

### Source ↔ runtime split

Bridges typically have source code that lives in your synced work folder (so you can edit from either machine) and a runtime copy that lives outside sync (so launchd can actually execute it). The pattern:

```
~/CC-WORK/db-utilities/telegram-bridge/     # Source, synced
  ├── bridge.py
  ├── run.sh
  └── requirements.txt

~/.telegram-bridge/                         # Runtime, local
  ├── bridge.py                             # Copy of source
  ├── run.sh
  ├── .env                                  # Secrets, never synced
  ├── venv/                                 # Python venv
  └── logs/
      ├── stdout.log
      └── stderr.log
```

The `services sync telegram-bridge` command in the services CLI rsyncs source → runtime, excluding `.env` (secrets stay local). After every source edit: `services sync telegram-bridge && services restart telegram-bridge`.

**Why not symlink runtime → source?** Three reasons: (1) launchd won't execute code from inside File Provider paths even via symlink, (2) sync daemons periodically touch files, which creates race conditions with any running process, (3) the venv is machine-local by definition (different architectures, different Python versions).

## IV. Scheduled tasks

Two mechanisms exist. Pick based on whether the task is a Claude-run skill or a raw script.

### Option A — Claude Code Desktop scheduled tasks

If the task is a SKILL.md that you want Claude to execute unattended, use Claude Code Desktop's built-in scheduler. The pattern:

1. Write the SKILL.md at `~/.claude/scheduled-tasks/<task-name>/SKILL.md`
2. Open Claude Code Desktop → Settings → Scheduled Tasks
3. Add a new task pointing at the SKILL.md, with a cron-like schedule
4. Set `permissionMode: "bypassPermissions"` on the task if it needs to run without prompting — essential for any unattended job

The task configuration is persisted in a file under `~/Library/Application Support/Claude/claude-code-sessions/<org-id>/<user-id>/scheduled-tasks.json`. Two keys matter for unattended runs: the global `bypassPermissionsModeEnabled` flag (enables the option at all) and per-task `permissionMode: "bypassPermissions"` (activates it for that task). **Both are required** — enabling one without the other silently does nothing.

The SKILL.md itself should:

* Start with a terse one-sentence purpose so the run log is readable
* Read from a project-config.json if it operates on a named project
* Write outputs to a project folder or a draft email, never to `/tmp/` (which vanishes on reboot and defeats auditability)
* End with a summary line that a human can scan at breakfast

Claude Code Desktop scheduled tasks are the right choice when the task is "read some stuff, think about it, write a draft email". They inherit your full skill library, so any work the task does can invoke your other skills.

### Option B — Raw LaunchAgent with `StartCalendarInterval`

If the task is a Python or shell script that doesn't need Claude's reasoning, a plain LaunchAgent is simpler:

```xml
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key><integer>4</integer>
  <key>Minute</key><integer>30</integer>
</dict>
```

**Do not use `StartInterval` + `KeepAlive` for scheduled jobs.** `KeepAlive` tells launchd to restart the job immediately when it exits, which turns "runs once a day at 04:30" into "runs forever starting at 04:30". If the job crashes, `KeepAlive` masks the failure as restarts. Reserve `KeepAlive` for bridges that are supposed to run forever.

For periodic-but-not-clock-based schedules ("every 15 minutes"), `StartInterval` *alone* (without `KeepAlive`) is correct: the job runs every N seconds but exits cleanly each time.

### Install manifest

Whichever option you pick, the installer should write an `install-manifest.json` to the runtime directory at install time, listing every path created. Example:

```json
{
  "installed_at": "2026-04-11T09:12:34Z",
  "label": "io.github.alice.claude-code-setup.email-nightly",
  "paths": [
    "/Users/alice/Library/LaunchAgents/io.github.alice.claude-code-setup.email-nightly.plist",
    "/Users/alice/.email-nightly/run.sh",
    "/Users/alice/.email-nightly/logs/",
    "/Users/alice/.email-nightly/venv/"
  ]
}
```

The uninstaller reads this back and removes only what the installer created. Never `sudo rm -rf` a path the user passed in. The manifest is the difference between a clean uninstall and leaving stray files for years.

## V. The `services` CLI

A small command-line tool that reads the registry and operates on services by ID. Canonical usage:

```bash
services                    # Status overview: each service with health / last-run / log tail
services logs <id>          # Tail that service's log
services restart <id>       # bootout then bootstrap
services sync <id>          # rsync source → runtime
services install <id>       # Create runtime dir, rsync source, write plist, bootstrap
services install --all      # Full machine setup — install every service in the registry
services uninstall <id>     # Read install-manifest.json, bootout, remove all listed paths
```

Implementation notes are in `bin/README.md`. The CLI itself is a single shell script (~200 lines) that parses the registry and dispatches to `launchctl` / `rsync` / `open`.

**Why machine-local, not synced?** The `services` CLI is installed at `~/bin/services` on each machine, not inside `~/CC-WORK/db-utilities/`. Two reasons: (1) it touches machine-specific paths (LaunchAgents live in `/Users/<you>/Library/LaunchAgents/`, which is local by definition), (2) on a fresh machine you need `services` before you've synced anything else, so it has to be installed first rather than last.

## VI. TCC Full Disk Access gotchas

This section will save you hours. macOS's Transparency, Consent, and Control (TCC) framework protects certain directories (Mail, Messages, Safari history, Calendar, Reminders) behind an explicit per-binary permission grant. Every service that touches those needs Full Disk Access, and the rules for what "a binary" means are subtler than they look.

### TCC identifies binaries by code signature + path

A LaunchAgent that runs `/opt/homebrew/bin/python3` has a different TCC identity from an interactive shell that runs the same `python3`. Grants from one context do not transfer to the other. This means:

* **Interactive (Terminal / Ghostty / iTerm) and headless (launchd) are separate TCC identities.** Granting FDA to your terminal app does not give launchd-run jobs FDA. You have to grant it to the specific binary launchd invokes.
* **After `brew upgrade`, TCC grants keyed to `/opt/homebrew/Cellar/<tool>/<version>/bin/<tool>` silently invalidate.** The path changes on upgrade, and TCC doesn't notify you — the job just starts failing.

### Two mitigations

**Point plists at symlinks, not versioned paths.** Use `/opt/homebrew/bin/python3`, never `/opt/homebrew/Cellar/python@3.12/3.12.8/bin/python3`. The symlink survives `brew upgrade`; the Cellar path doesn't.

**Document re-granting in your installer's README.** Tell users the first run after `brew upgrade` may need a fresh FDA grant. Provide the one-liner to open the right Settings pane:

```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
```

These URL schemes are [publicly documented](https://gist.github.com/rmcdongit/f66ff91e0dad78d4d6346a75ded4b751) and much friendlier than "open System Settings, click Privacy & Security, scroll to Full Disk Access, click the `+` button".

### Pre-flight TCC probe

Before a service does anything destructive, probe a protected path:

```bash
if ! cat ~/Library/Mail/V*/MailData/Envelope\ Index > /dev/null 2>&1; then
  echo "ERROR: Full Disk Access is not granted to $0 (or the binary that launched it)."
  echo "Open System Settings and grant FDA, then re-run this service."
  echo "Shortcut: open 'x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles'"
  exit 1
fi
```

The probe fails noisily at install time instead of silently at 04:30 the next morning.

### Don't touch the TCC database directly

Some older guides suggest editing `/Library/Application Support/com.apple.TCC/TCC.db`. Don't. System Integrity Protection guards it, and anything you read is a cache that can diverge from the actual grant state. If you need to *verify* a grant from a script, use the pre-flight probe pattern above, not a SQL query.

### launchd pseudo-TTY for CLI tools that detect it

Some CLI tools (including `claude` in its interactive mode) check whether stdin is a TTY and change behaviour accordingly. Under launchd there is no TTY, which sometimes puts the tool into `--print` mode when you wanted interactive mode. The workaround is `script`:

```bash
script -q /dev/null /path/to/inner.sh
```

`script` allocates a pseudo-TTY that satisfies the `[ -t 0 ]` check. Use this wrapper in any LaunchAgent that calls a CLI tool with TTY-dependent behaviour.

## VII. What to sync, what to keep local

With multi-machine setups (Dropbox, iCloud, Syncthing, etc.), the rule is: **sync definitions, keep runtimes local.**

| Sync between machines | Keep local |
|---|---|
| `~/.claude/services/registry.json` | `~/Library/LaunchAgents/<label>.plist` |
| Service source code in `~/CC-WORK/db-utilities/<service>/` | Service runtime in `~/.<service>/` |
| The `services` CLI (installed via your dotfile tooling) | Secrets in runtime `.env` files |
| `~/.claude/scheduled-tasks/<task>/SKILL.md` | `~/Library/Application Support/Claude/...scheduled-tasks.json` |

The principle: a new machine should be able to clone your setup, run `services install --all`, and end up with every registered service running — but the registry describes *what to install*, not the actual installed state. Plists, venvs, logs, and secrets are per-machine and never travel.

**Sync storm avoidance.** Runtime directories accumulate log files, venv updates, and SQLite state — exactly the kind of high-frequency write pattern that causes sync daemons to melt. Keeping them outside sync entirely is the single biggest win for sync reliability. If you must keep something venv-like inside a synced folder, use the `.nosync` suffix pattern (iCloud respects it natively; Dropbox needs both a `rules.dropboxignore` entry and a per-folder xattr).

## VIII. Related files in this repo

* `bin/README.md` — the `services`, `secret`, `dbx-materialize`, `dgit`, `chrome-debug` helper scripts
* `mcp-servers/README.md` — MCP servers, a different kind of "always-on" that lives inside Claude Code rather than as a LaunchAgent
* `settings/HOOKS-EXAMPLES.md` — hooks fire on Claude Code events and live in `settings.json`; they're not services but sit adjacent to the notification patterns this guide references
* `skills/needs-credentials/work-nightly/` (to be added in a later phase) — a concrete example of the scheduled-task pattern applied to nightly email triage

## IX. Further reading

* [launchd.info](https://www.launchd.info/) — the canonical plist reference
* [Homebrew services PR #112](https://github.com/Homebrew/homebrew-services/pull/112) — the migration from `load`/`unload` to `bootstrap`/`bootout`
* [Sam Nunn — TCC and launchd woes](https://nunn.au/2023/11/28/tcc-launchd-woes) — the best write-up of the interactive-vs-headless TCC identity problem
* [clig.dev](https://clig.dev/) — CLI guidelines used throughout this repo's helper scripts
* [macOS System Settings URL schemes](https://gist.github.com/rmcdongit/f66ff91e0dad78d4d6346a75ded4b751) — for the `open "x-apple.systempreferences:..."` one-liners in §VI
