# Claude Code Permissions Guide

How to configure what Claude Code can do without asking.

## Overview

Claude Code asks permission before:
- Running bash commands
- Accessing websites
- Reading/writing files outside the project
- Using skills

You can pre-approve actions by adding them to `~/.claude/settings.json`.

## Basic Structure

```json
{
  "permissions": {
    "allow": [
      "// Category comment",
      "Pattern(scope)",
      "Pattern(scope)"
    ]
  }
}
```

**Comments:** Lines starting with `//` are ignored. Use them to organize.

## Permission Patterns

### Bash Commands

```json
"Bash(command:*)"        // Any arguments to command
"Bash(git:*)"            // All git operations
"Bash(npm:*)"            // All npm operations
"Bash(python3:*)"        // All python3 scripts
"Bash(~/bin/*)"          // Scripts in your bin folder
```

**The `*` wildcard** matches any arguments.

### Web Access

```json
"WebFetch(domain:github.com)"           // Single domain
"WebFetch(domain:docs.python.org)"      // Documentation sites
"WebFetch(domain:api.openai.com)"       // API endpoints
```

**Note:** Subdomains require separate entries. `github.com` doesn't include `api.github.com`.

### File Writes

```json
"Write(~/.claude/*)"     // Claude's own config
"Write(/tmp/*)"          // Temp files
"Write(~/projects/*)"    // Your projects folder
```

**Be careful:** Don't add `Write(~/*)`—that's too broad.

### Skills

```json
"Skill(skill-name)"      // Specific skill
"Skill(*)"               // All skills (not recommended)
```

### MCP Tools

```json
"mcp__server__tool"      // Specific MCP tool
```

## Recommended Starting Set

```json
{
  "permissions": {
    "allow": [
      "// Git",
      "Bash(git:*)",
      "Bash(gh:*)",

      "// Package managers",
      "Bash(npm:*)",
      "Bash(pip3:*)",

      "// Python",
      "Bash(python3:*)",

      "// File operations",
      "Bash(ls:*)",
      "Bash(mkdir:*)",
      "Bash(cp:*)",
      "Bash(mv:*)",

      "// macOS",
      "Bash(open:*)",

      "// Common domains",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:stackoverflow.com)",

      "// Claude config",
      "Write(~/.claude/*)"
    ]
  }
}
```

## Settings Files

### settings.json (Global)

Location: `~/.claude/settings.json`

Contains:
- Permission allow-list
- Environment variables
- Hooks
- Plugin configuration

**Syncs between machines:** If you use cloud sync, this file can be shared.

### settings.local.json (Machine-specific)

Location: `~/.claude/settings.local.json`

Contains:
- Machine-specific overrides
- Local paths
- Accumulated permissions from prompts

**Does NOT sync:** Keep this machine-specific.

## Adding Permissions Incrementally

When Claude asks permission:
1. Approve the action
2. Choose "Always allow" if it's something you'll use often
3. The permission is added to `settings.local.json`

Periodically review `settings.local.json` and move useful patterns to `settings.json`.

## Cleaning Up Permissions

Over time, `settings.local.json` accumulates cruft:
- One-time commands
- Debug fragments
- Project-specific paths

**Quarterly cleanup:**
1. Open `settings.local.json`
2. Remove project-specific entries
3. Remove one-time commands
4. Move frequently-used patterns to `settings.json`

## Environment Variables

Add environment variables for skills:

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-...",
    "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}"
  }
}
```

**Better approach:** Set in shell profile (`~/.zshrc`) instead:
```bash
export ANTHROPIC_API_KEY=$(cat ~/.config/secrets/anthropic-api-key)
```

This keeps credentials out of settings files.

## Tips

### Start Restrictive, Loosen as Needed
Don't add `Bash(*)`. Start with specific commands and expand.

### Organize with Comments
Use `//` comments to group related permissions. Future-you will thank you.

### Separate Global vs Local
- `settings.json`: Patterns you want everywhere
- `settings.local.json`: Machine-specific, accumulated

### Check Syntax
Invalid JSON breaks permissions. Use `jq . ~/.claude/settings.json` to validate.

### Backup Before Major Changes
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.backup
```
