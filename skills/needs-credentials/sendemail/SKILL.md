---
name: sendemail
description: |
  Send email notifications via Gmail SMTP. Use when: completing long-running tasks,
  reporting results that need attention, sending summaries or reports, or when
  explicitly asked to email something.
---

# Send Email

Send emails using Gmail SMTP.

## Setup

Requires:
1. Gmail account with App Password enabled (see SETUP.md)
2. The sendemail script installed at `~/.claude/bin/sendemail`

## Usage

```bash
~/.claude/bin/sendemail --subject "Subject line" --body "Message body"
```

## Options

| Flag | Description |
|------|-------------|
| `--subject`, `-s` | Email subject (required) |
| `--body`, `-b` | Message body text |
| `--body-file`, `-f` | Read body from file |
| `--to`, `-t` | Recipient email address |

## Examples

```bash
# Simple notification
~/.claude/bin/sendemail -s "Task complete" -b "Build finished successfully."

# From file
~/.claude/bin/sendemail -s "Daily Report" -f /path/to/report.txt

# Piped content
echo "Results: 47 files processed" | ~/.claude/bin/sendemail -s "Processing done"
```

## When to Use

- After long-running tasks complete (builds, scrapes, analyses)
- When results need the user's attention
- Sending reports or summaries
- When user explicitly asks to "email me" something

## Compared to Other Notifications

| Method | Use Case |
|--------|----------|
| **sendemail** | Detailed reports, results that need review later |
| **imessage** | Quick alerts, time-sensitive notifications (macOS only) |
| **callme** | Interactive discussion, blocking questions (Telegram) |

## Configuration

The script reads credentials from:
- `~/.config/secrets/gmail-app-password` — Your Gmail app password
- `~/.config/secrets/gmail-sender-email` — Your Gmail address (or hardcode in script)

See SETUP.md for credential configuration.
