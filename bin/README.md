# Helper Scripts

Shell scripts that extend Claude Code's capabilities.

## Overview

These scripts live in `~/.claude/bin/` and are called from skills or directly.

## Scripts in This Repository

### sendemail-template

A template for sending emails via Gmail SMTP.

**Setup required:** See `skills/needs-credentials/sendemail/SETUP.md`

**Usage:**
```bash
~/.claude/bin/sendemail -s "Subject" -b "Message body"
```

## Creating Your Own Scripts

### Location

Put scripts in `~/.claude/bin/`:
```bash
mkdir -p ~/.claude/bin
```

### Make Executable

```bash
chmod +x ~/.claude/bin/your-script
```

### Permissions

Add to `settings.json`:
```json
"Bash(~/.claude/bin/*)"
```

Or specific scripts:
```json
"Bash(~/.claude/bin/sendemail:*)"
```

### Best Practices

1. **Use full paths in scripts** — Don't rely on PATH
2. **Read credentials from files** — Not hardcoded
3. **Add usage help** — `--help` flag
4. **Handle errors gracefully** — Exit codes and messages

### Template Script

```bash
#!/bin/bash
# Description: What this script does
# Usage: script-name [options]

set -e  # Exit on error

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: script-name [options]"
            echo "Options:"
            echo "  -h, --help    Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Your script logic here
echo "Done!"
```

## Integration with Skills

Skills can call scripts:

```markdown
## Usage

\`\`\`bash
~/.claude/bin/your-script --option value
\`\`\`
```

Claude will run the script when the skill is invoked.

## Syncing Scripts

If you use Dropbox/iCloud for multi-machine sync:

```bash
# Store scripts in synced location
mkdir -p ~/Dropbox/.claude-sync/bin

# Symlink to standard location
ln -s ~/Dropbox/.claude-sync/bin ~/.claude/bin
```

Both machines can then use the same scripts.
