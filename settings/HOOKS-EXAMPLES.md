# Claude Code Hooks Examples

How to get notified when Claude Code needs attention.

## Overview

Hooks run shell commands when specific events happen:
- Permission prompts (Claude is waiting)
- Idle timeouts (Claude has been waiting)
- Task completion
- Errors

## Basic Structure

In `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "event_type",
        "hooks": [
          {
            "type": "command",
            "command": "your-notification-command"
          }
        ]
      }
    ]
  }
}
```

## Event Types

| Matcher | When it fires |
|---------|---------------|
| `permission_prompt` | Claude needs approval to continue |
| `idle_prompt` | Claude has been waiting (timeout) |

## Example: macOS Notification

Use `osascript` to show a native notification:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs permission\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

## Example: Play a Sound

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Ping.aiff"
          }
        ]
      }
    ]
  }
}
```

## Example: iMessage Notification

If you have an iMessage CLI tool:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/imsg send --to '+1234567890' --text '🔔 Claude needs permission'"
          }
        ]
      }
    ]
  }
}
```

**Important:** Use full paths, not `~` — shell expansion doesn't work in hooks.

## Example: Telegram Notification

Using curl to send a Telegram message:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "curl -s -X POST 'https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage' -d 'chat_id=${TELEGRAM_CHAT_ID}&text=🔔 Claude needs permission'"
          }
        ]
      }
    ]
  }
}
```

## Example: Multiple Hooks

Run multiple commands for the same event:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Ping.aiff"
          },
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude waiting\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

## Example: Different Hooks for Different Events

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Needs permission\" with title \"Claude Code\"'"
          }
        ]
      },
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/imsg send --to '+1234567890' --text '⏰ Claude has been idle'"
          }
        ]
      }
    ]
  }
}
```

## Tips

### Use Full Paths
Hooks don't have your shell profile. Use `/usr/bin/curl` not just `curl`.

### Test Commands First
Run the notification command manually before adding to hooks:
```bash
afplay /System/Library/Sounds/Ping.aiff
```

### Escape Quotes Carefully
JSON requires escaping. Test with `jq . settings.json` to validate.

### Keep Hooks Fast
Hooks run synchronously. Slow hooks delay Claude. Keep commands under 1 second.

### Consider Sound + Visual
Sound catches attention even when you're not looking. Combine with visual notification:
```json
{
  "type": "command",
  "command": "afplay /System/Library/Sounds/Ping.aiff & osascript -e 'display notification \"Claude waiting\" with title \"Claude Code\"'"
}
```

## Troubleshooting

### Hook Not Firing
1. Check JSON syntax: `jq . ~/.claude/settings.json`
2. Verify `matcher` spelling
3. Restart Claude Code after changes

### Command Fails
1. Test command in terminal first
2. Check full path is correct
3. Verify permissions: `chmod +x /path/to/script`

### Environment Variables Not Working
Hooks don't inherit your shell environment. Either:
- Hardcode values
- Read from file: `$(cat ~/.config/secrets/token)`
- Use a wrapper script
