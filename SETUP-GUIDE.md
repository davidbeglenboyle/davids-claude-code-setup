# Claude Code Setup Guide

How to install Claude Code and configure it using the patterns in this repository.

## I. Installation

### A. Install Claude Code

```bash
# macOS / Linux
npm install -g @anthropic-ai/claude-code

# Or via Homebrew (macOS)
brew install claude-code
```

### B. First Run

```bash
claude
```

On first run, Claude Code creates `~/.claude/` with:
- `settings.json` — permissions and configuration
- `settings.local.json` — machine-specific overrides
- `CLAUDE.md` — your personal instructions (optional but recommended)
- `skills/` — custom skills directory

### C. Authenticate

Claude Code prompts for your Anthropic API key on first use. Store it securely:

```bash
# Option 1: Environment variable (recommended)
export ANTHROPIC_API_KEY="sk-..."

# Option 2: Let Claude Code prompt you (stored in keychain)
```

## II. Directory Structure

After setup, your Claude Code files live here:

```
~/.claude/
├── CLAUDE.md              # Your personal instructions
├── settings.json          # Global permissions
├── settings.local.json    # Machine-specific overrides
├── rules/                 # Domain-specific instructions (auto-loaded)
│   ├── data-analysis.md
│   ├── secrets-management.md
│   └── ...
├── skills/                # Custom skills
│   ├── skill-name/
│   │   └── SKILL.md
│   └── ...
├── agents/                # Sub-agent definitions (used by skills)
│   ├── deliverable-critic.md
│   └── deliverable-fixer.md
└── projects/              # Session transcripts (auto-generated)
```

## III. Setting Up Rules (Optional)

Rules files split domain-specific instructions out of CLAUDE.md. Skip this if your CLAUDE.md is under 300 lines.

```bash
# Create the rules directory
mkdir -p ~/.claude/rules

# Copy templates (remove "-template" suffix)
cp rules/data-analysis-template.md ~/.claude/rules/data-analysis.md
cp rules/secrets-management-template.md ~/.claude/rules/secrets-management.md
cp rules/document-production-template.md ~/.claude/rules/document-production.md
cp rules/technical-patterns-template.md ~/.claude/rules/technical-patterns.md
```

Edit each file to match your tools and workflows. Claude Code loads all files in `~/.claude/rules/` automatically.

See `rules/README.md` for details on conditional loading and best practices.

## IV. Installing Skills

### From This Repository

Copy skill folders into `~/.claude/skills/`:

```bash
# Single skill
cp -r skills/ready-to-use/chart-design ~/.claude/skills/

# All ready-to-use skills
cp -r skills/ready-to-use/* ~/.claude/skills/
```

### From Anthropic's Plugin Marketplace

In Claude Code:
```
/plugins install legal
/plugins install data-analysis
```

### Verifying Installation

```bash
ls ~/.claude/skills/
```

Skills appear in Claude Code's skill list automatically.

## V. Setting Up CLAUDE.md

### Start from Template

```bash
cp claude-md/CLAUDE-TEMPLATE.md ~/.claude/CLAUDE.md
```

### Customise Sections

Edit `~/.claude/CLAUDE.md` and fill in:
1. **Professional Context** — Your role, expertise, company
2. **Personal Context** — Optional working patterns, location
3. **Project Contacts** — Key people you work with
4. **Communication Preferences** — Tone, formatting, style

See `claude-md/SECTIONS-EXPLAINED.md` for what each section does.

## VI. Credential Management

### The Problem

Putting API keys directly in SKILL.md files or settings.json means:
- Credentials sync to backups (risky)
- Sharing skills exposes secrets
- No single place to rotate keys

### The Solution: Indirection

Skills reference a *path* to credentials, not the credentials themselves:

```markdown
## Credentials
Reads token from `~/.config/secrets/telegram-bot-token`
```

### Setup Steps

1. **Create secrets directory:**
   ```bash
   mkdir -p ~/.config/secrets
   chmod 700 ~/.config/secrets
   ```

2. **Add credentials as plain files:**
   ```bash
   echo "sk-ant-..." > ~/.config/secrets/anthropic-api-key
   echo "1234567890:AAH..." > ~/.config/secrets/telegram-bot-token
   chmod 600 ~/.config/secrets/*
   ```

3. **Load in shell profile (optional but recommended):**
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export ANTHROPIC_API_KEY=$(cat ~/.config/secrets/anthropic-api-key 2>/dev/null)
   ```

### Multi-Machine Sync

For multi-machine setups, see `STORAGE-OPTIONS.md`.

## VII. Permissions Configuration

### Understanding Permissions

Claude Code asks permission before:
- Running bash commands
- Accessing websites
- Reading/writing files outside the project

### Building Your Allow-List

Edit `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "// Git operations",
      "Bash(git:*)",

      "// Package managers",
      "Bash(npm:*)",
      "Bash(pip:*)",

      "// Your custom scripts",
      "Bash(~/bin/*)",

      "// Web access",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:stackoverflow.com)"
    ]
  }
}
```

See `settings/PERMISSIONS-GUIDE.md` for detailed patterns.

## VIII. Notification Hooks

Get notified when Claude Code needs attention:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "your-notification-script 'Claude needs permission'"
          }
        ]
      }
    ]
  }
}
```

See `settings/HOOKS-EXAMPLES.md` for iMessage, Telegram, and other integrations.

## IX. Installing quality-score (Optional)

A mechanical pre-flight check for deliverables:

```bash
# Copy to your PATH
cp bin/quality-score ~/bin/
chmod +x ~/bin/quality-score

# Test it
quality-score README.md
```

Add client brand rubrics by editing the `BRAND_RUBRICS` dict at the top of the script.

## X. Troubleshooting

### Skills Not Appearing

1. Check folder structure: `~/.claude/skills/skill-name/SKILL.md`
2. Verify SKILL.md has valid frontmatter
3. Restart Claude Code

### Permission Errors

1. Check `settings.json` syntax (valid JSON?)
2. Look for typos in permission patterns
3. Try broader pattern temporarily: `"Bash(*)"` (then narrow down)

### Credentials Not Loading

1. Check file exists: `ls -la ~/.config/secrets/`
2. Check permissions: `chmod 600 ~/.config/secrets/*`
3. Source shell profile: `source ~/.zshrc`

## XI. Next Steps

1. **Browse skills** — See what's available in `skills/`
2. **Customise CLAUDE.md** — Make Claude Code work your way
3. **Set up notifications** — Never miss a permission prompt
4. **Explore Anthropic plugins** — `/plugins list` in Claude Code
