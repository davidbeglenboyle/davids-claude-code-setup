# MCP Servers

Model Context Protocol servers extend Claude Code with additional capabilities.

## What are MCP Servers?

MCP (Model Context Protocol) servers provide:
- Additional tools for Claude to use
- Access to external services
- Custom integrations

Claude Code discovers MCP servers and makes their tools available.

## MCP Servers Used in This Setup

### callme (Telegram)

**Purpose:** Send messages and receive responses via Telegram.

**Tools provided:**
- `mcp__callme__initiate_call` — Start conversation
- `mcp__callme__continue_call` — Send follow-up
- `mcp__callme__speak_to_user` — Send without waiting
- `mcp__callme__end_call` — End conversation

**Setup:** See `skills/needs-credentials/callme/SETUP.md`

### Claude in Chrome

**Purpose:** Browser automation and web interaction.

**Tools provided:**
- `mcp__claude-in-chrome__navigate` — Open URLs
- `mcp__claude-in-chrome__read_page` — Get page content
- `mcp__claude-in-chrome__computer` — Click, type, screenshot
- And more...

**Setup:** Install the Claude in Chrome extension from the Chrome Web Store.

### Reddit MCP Buddy

**Purpose:** Read and search Reddit.

**Tools provided:**
- `mcp__reddit-mcp-buddy__browse_subreddit`
- `mcp__reddit-mcp-buddy__search_reddit`
- `mcp__reddit-mcp-buddy__get_post_details`
- `mcp__reddit-mcp-buddy__user_analysis`

**Setup:** Install from MCP server repository.

## Installing MCP Servers

### From npm

```bash
npm install -g @anthropic/mcp-server-name
```

### From GitHub

```bash
git clone https://github.com/org/mcp-server
cd mcp-server
npm install
npm link
```

## Configuration

MCP servers are configured in Claude Code's settings or a dedicated config file.

**Example in settings.json:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/path/to/server/index.js"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

## Checking Available Servers

In Claude Code:
```
/mcp
```

This shows all connected MCP servers and their tools.

## Creating Custom MCP Servers

For custom integrations, you can create your own MCP servers:

1. Use the MCP SDK
2. Define tools with schemas
3. Handle tool calls
4. Run as a background process

**Resources:**
- [MCP Specification](https://modelcontextprotocol.io/)
- [Anthropic MCP SDK](https://github.com/anthropics/mcp)

## Troubleshooting

### Server Not Connecting
1. Check the server is running: `ps aux | grep mcp`
2. Verify configuration path
3. Check environment variables

### Tools Not Appearing
1. Restart Claude Code
2. Run `/mcp` to see connected servers
3. Check server logs for errors

### Permission Errors
Add tools to your allow-list:
```json
"mcp__servername__toolname"
```

Or all tools from a server:
```json
"mcp__servername__*"
```
