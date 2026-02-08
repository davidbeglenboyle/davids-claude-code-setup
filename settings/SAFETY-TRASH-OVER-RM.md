# Safety: Use `trash` Instead of `rm`

By default, Claude Code can permanently delete files if `Bash(rm:*)` is in your allow list. This guide explains the risk and how to fix it.

## The Problem

Unix `rm` permanently removes files. There is no Trash, no undo, no recovery. When Claude Code has `Bash(rm:*)` auto-approved, it can delete any file on your system without asking.

macOS provides `/usr/bin/trash`, which moves files to `~/.Trash` instead — exactly like dragging to Trash in Finder. Files remain recoverable until you empty Trash.

## The Fix

### 1. Claude Code Settings

In `~/.claude/settings.json`:

**Remove from allow list:**
```json
"Bash(rm:*)"
```

**Add to allow list:**
```json
"Bash(trash:*)"
```

**Add a deny list** (blocks `rm` entirely, not just unapproved):
```json
"deny": [
  "Bash(rm:*)",
  "Bash(rm -rf:*)",
  "Bash(rm -r:*)"
]
```

### 2. Shell Alias (Optional but Recommended)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Safety: rm → trash (moves to macOS Trash instead of permanent deletion)
# Use 'command rm' or '/bin/rm' when you genuinely need permanent deletion
alias rm='trash'
```

This protects your own terminal use too. Muscle memory types `rm` — the alias catches it.

### 3. CLAUDE.md Guidance (Optional)

Add to your CLAUDE.md so Claude uses `trash` by default even without the deny list:

```markdown
* Always use `trash` instead of `rm` for file removal — files go to macOS Trash, not permanent deletion
```

## How It Works

| Command | Effect | Recoverable? |
|---------|--------|--------------|
| `rm file.txt` | Removes directory entry; data lost | No |
| `trash file.txt` | Moves to `~/.Trash/` | Yes, until emptied |
| `command rm file.txt` | Bypasses alias, permanent delete | No |
| `/bin/rm file.txt` | Bypasses alias, permanent delete | No |

## Why Deny, Not Just Remove?

If `rm` is simply removed from the allow list (rather than denied), Claude Code will prompt for permission each time. You might reflexively approve. The deny list makes the wrong action impossible rather than merely inconvenient.

## Escape Hatches

When you genuinely need permanent deletion (clearing large temp files, etc.):

- **In terminal:** `command rm file.txt` or `/bin/rm file.txt` bypasses the alias
- **In Claude Code:** You would need to temporarily remove `rm` from the deny list, which is deliberately inconvenient — the friction is the feature

## Platform Notes

- **macOS:** Ships with `/usr/bin/trash`. No installation needed.
- **Linux:** Install `trash-cli` (`sudo apt install trash-cli` or equivalent). The command is `trash-put` instead of `trash`.
- **Homebrew alternative:** `brew install macos-trash` provides additional features but the built-in `/usr/bin/trash` is sufficient.
