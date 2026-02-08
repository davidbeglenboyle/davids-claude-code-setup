# Storage Options for Multi-Machine Claude Code

How to sync your Claude Code setup across multiple computers.

## I. Single Machine (Simplest)

If you only use Claude Code on one computer:

- Store everything in `~/.claude/`
- Credentials in `~/.config/secrets/`
- No sync needed

**Pros:** No complexity, no sync conflicts
**Cons:** Setup doesn't transfer to new machines

## II. Cloud Sync Services

### Comparison

| Service | Pros | Cons | Best for |
|---------|------|------|----------|
| **Dropbox** | Reliable, selective sync, LAN sync | Paid for larger storage | Power users needing offline access |
| **iCloud Drive** | Built into macOS, free 5GB | Unreliable with small files, macOS only | Apple-only setups |
| **OneDrive** | Included with Microsoft 365 | Can be slow, aggressive sync | Microsoft 365 users |
| **Google Drive** | 15GB free, good web UI | Desktop app less polished | Google Workspace users |
| **Syncthing** | Self-hosted, encrypted, no cloud | Requires setup, needs both machines online | Privacy-focused users |

### What to Sync vs. Keep Local

| Sync Between Machines | Keep Local (Machine-Specific) |
|-----------------------|-------------------------------|
| `~/.claude/skills/` | `~/.claude/settings.local.json` |
| `~/.claude/rules/` | `~/.claude/statsCache.json` |
| `~/.claude/CLAUDE.md` | `~/.claude/projects/` (transcripts) |
| `~/.config/secrets/` | Some OAuth tokens |
| Custom bin scripts | |

**Why keep transcripts local?** They're large, machine-specific, and often contain sensitive project context. Back up separately if needed.

**Why keep settings.local.json local?** It contains machine-specific paths and accumulated permissions. Let each machine have its own.

## III. The Symlink Pattern

The key to multi-machine sync: **symlinks**. Your tools expect files in standard locations (`~/.claude/`), but the actual files live in your sync folder.

### Basic Setup (Dropbox Example)

```bash
# 1. Create sync folder (hidden with dot prefix)
mkdir -p ~/Dropbox/.claude-sync/{skills,secrets}

# 2. Move files to sync folder
mv ~/.claude/skills/* ~/Dropbox/.claude-sync/skills/
mv ~/.config/secrets/* ~/Dropbox/.claude-sync/secrets/

# 3. Create symlinks
ln -s ~/Dropbox/.claude-sync/skills ~/.claude/skills
ln -s ~/Dropbox/.claude-sync/secrets ~/.config/secrets
```

### On Second Machine

```bash
# Just create symlinks (files already synced)
ln -s ~/Dropbox/.claude-sync/skills ~/.claude/skills
ln -s ~/Dropbox/.claude-sync/secrets ~/.config/secrets
```

### Verifying Symlinks

```bash
ls -la ~/.claude/skills
# Should show: skills -> /Users/you/Dropbox/.claude-sync/skills
```

## IV. What to Sync

### Recommended Sync Folder Structure

```
~/Dropbox/.claude-sync/          # Or your sync service
├── skills/                       # All custom skills
│   ├── chart-design/
│   ├── frontend-design/
│   └── ...
├── rules/                        # Domain-specific instructions
│   ├── data-analysis.md
│   └── ...
├── secrets/                      # Credentials
│   ├── anthropic-api-key
│   ├── telegram-bot-token
│   └── google-calendar/
├── CLAUDE.md                     # Global instructions
└── bin/                          # Helper scripts
    ├── quality-score
    └── sendemail
```

### Symlinks to Create

| Standard Location | Synced Location |
|-------------------|-----------------|
| `~/.claude/skills` | `~/Dropbox/.claude-sync/skills` |
| `~/.claude/rules` | `~/Dropbox/.claude-sync/rules` |
| `~/.claude/CLAUDE.md` | `~/Dropbox/.claude-sync/CLAUDE.md` |
| `~/.config/secrets` | `~/Dropbox/.claude-sync/secrets` |

## V. OAuth Token Considerations

### Tokens That DON'T Sync Well

Some OAuth tokens include machine-specific information:

- **Google Calendar/Docs tokens** — May include device identifiers
- **GitHub CLI tokens** — Tied to specific machine authentication

**Solution:** Re-authenticate on each machine. The OAuth *credentials* (client ID, client secret) can sync, but the *tokens* should be generated fresh.

### Tokens That Sync Fine

- **API keys** (Anthropic, OpenAI, etc.) — Just strings
- **Bot tokens** (Telegram, Slack) — Not machine-specific
- **App passwords** (Gmail SMTP) — Not machine-specific

## VI. Avoiding Sync Conflicts

### The .nosync Pattern (Dropbox/iCloud)

Some files shouldn't sync even within a synced folder. Both Dropbox and iCloud respect the `.nosync` suffix:

```bash
# This folder syncs
~/Dropbox/.claude-sync/skills/

# This won't (even inside a synced folder)
~/Dropbox/.claude-sync/skills/.venv.nosync/
```

Use for: virtual environments, node_modules, build artifacts.

### Preventing Conflict Files

1. **Don't edit the same skill on two machines simultaneously**
2. **Use settings.local.json for machine-specific settings** (not synced)
3. **If you see "Conflicted copy" files**, merge manually and delete duplicates

## VII. Platform-Specific Notes

### macOS + iCloud

iCloud Drive can be unreliable with small config files:
- Sync delays for tiny files
- "Optimise Mac Storage" can evict files when disk is full

**Recommendation:** For Claude Code, prefer Dropbox or local-only over iCloud.

### Linux

Most cloud services have unofficial Linux clients:
- **Dropbox:** Official client available
- **OneDrive:** Use `rclone` or `onedriver`
- **iCloud:** Use `icloud-drive-fuse` (unofficial)
- **Syncthing:** Native Linux support (recommended for Linux users)

### Windows + WSL

If using Claude Code in WSL:
- Windows cloud clients don't see WSL filesystem
- Mount Windows sync folder into WSL:
  ```bash
  ln -s /mnt/c/Users/You/Dropbox/.claude-sync ~/.claude-sync
  ```

## VIII. Backup Strategy

Even with cloud sync, maintain backups:

### Simple: Archive periodically

```bash
# Monthly backup
tar -czvf claude-backup-$(date +%Y-%m).tar.gz \
  ~/.claude/skills \
  ~/.claude/CLAUDE.md \
  ~/.config/secrets
```

### Better: Git for skills

```bash
cd ~/.claude/skills
git init
git add -A
git commit -m "Skills backup $(date +%Y-%m-%d)"
```

**Warning:** Don't commit credentials. Use `.gitignore` to exclude `secrets/`.

## IX. Troubleshooting

### Symlink Points to Wrong Location

```bash
# Check where it points
ls -la ~/.claude/skills

# Fix by removing and recreating
rm ~/.claude/skills
ln -s ~/Dropbox/.claude-sync/skills ~/.claude/skills
```

### Files Not Syncing

1. Check sync client is running
2. Check file isn't in a `.nosync` folder
3. Check disk isn't full
4. Force sync: `dropbox.py status` (Dropbox CLI)

### Permission Denied After Sync

Cloud services sometimes lose Unix permissions:

```bash
chmod 600 ~/.config/secrets/*
chmod 755 ~/.claude/bin/*
```
