# Callme Skill Setup (Telegram)

How to set up Telegram bot integration for Claude Code notifications.

## Overview

This skill uses a Telegram bot to send messages and receive responses. You'll need:
1. A Telegram bot (created via BotFather)
2. Your chat ID (where messages should go)
3. The callme MCP server running

## Setup Steps

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow prompts:
   - Choose a name for your bot (e.g., "My Claude Code Bot")
   - Choose a username (must end in `bot`, e.g., `my_claudecode_bot`)
4. BotFather gives you an **API token** like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Save this token securely

### 2. Get Your Chat ID

1. Start a conversation with your new bot (search for it in Telegram, click Start)
2. Send any message to it
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}` in the response
5. That number is your chat ID

**Alternative method:**
1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. It replies with your user ID

### 3. Store Credentials

Save credentials in your secrets directory:

```bash
# Create secrets directory if needed
mkdir -p ~/.config/secrets

# Save bot token
echo "YOUR_BOT_TOKEN_HERE" > ~/.config/secrets/telegram-bot-token
chmod 600 ~/.config/secrets/telegram-bot-token

# Save chat ID
echo "YOUR_CHAT_ID_HERE" > ~/.config/secrets/telegram-chat-id
chmod 600 ~/.config/secrets/telegram-chat-id
```

### 4. Configure Claude Code

Add environment variables to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export CALLME_TELEGRAM_BOT_TOKEN=$(cat ~/.config/secrets/telegram-bot-token)
export CALLME_TELEGRAM_CHAT_ID=$(cat ~/.config/secrets/telegram-chat-id)
export CALLME_MESSAGE_TIMEOUT_SECONDS=600  # Optional: default 10 minutes
```

Or add to Claude Code's settings.json:

```json
{
  "env": {
    "CALLME_TELEGRAM_BOT_TOKEN": "YOUR_TOKEN_HERE",
    "CALLME_TELEGRAM_CHAT_ID": "YOUR_CHAT_ID_HERE",
    "CALLME_MESSAGE_TIMEOUT_SECONDS": "600"
  }
}
```

**Note:** Prefer the shell profile method — it keeps credentials out of settings.json.

### 5. Install MCP Server

The callme skill requires the callme MCP server. Install it:

```bash
# If using npm
npm install -g @anthropic/mcp-callme

# Or check Anthropic's MCP server repository for latest installation method
```

Add to your MCP configuration (typically in Claude Code settings or a dedicated MCP config file).

### 6. Test the Setup

In Claude Code, the callme tools should now be available:
- `mcp__callme__initiate_call`
- `mcp__callme__continue_call`
- `mcp__callme__speak_to_user`
- `mcp__callme__end_call`

Try asking Claude Code to message you on Telegram.

## Multi-Machine Setup

Bot tokens and chat IDs are not machine-specific — sync them:

```bash
# Store in synced secrets directory
echo "YOUR_TOKEN" > ~/Dropbox/.secrets/telegram-bot-token
echo "YOUR_CHAT_ID" > ~/Dropbox/.secrets/telegram-chat-id

# Symlink to standard location
ln -s ~/Dropbox/.secrets ~/.config/secrets
```

Both machines can then use the same bot.

## Troubleshooting

### "Bot not responding"
1. Verify you started a conversation with the bot (sent `/start`)
2. Check the token is correct
3. Ensure the MCP server is running

### "Chat ID not found"
1. Send a message to your bot first
2. Check getUpdates endpoint again
3. Make sure you're using the chat ID, not the user ID (they're often the same but not always)

### "Timeout waiting for response"
1. Increase `CALLME_MESSAGE_TIMEOUT_SECONDS`
2. Check your internet connection
3. Verify Telegram isn't blocked on your network

## AI Agent Instructions

When setting this up via Claude Code:

1. Cannot create the bot — user must do this via BotFather
2. Cannot get chat ID — user must message the bot first
3. Can help store credentials once user provides them
4. Can verify MCP server is configured correctly

Tell the user: "Please create a Telegram bot via @BotFather and send it a message. Then give me the bot token and your chat ID, and I'll help you configure everything."
