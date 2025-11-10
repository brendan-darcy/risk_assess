# MCP Server Configuration Template

This template is based on the actual MCP configuration used in our Claude Code setup.

## Configuration File

MCP servers are configured in:
- **User-level (Global)**: `~/.claude.json` (applies to all projects)
  - Contains the `mcpServers` key with server definitions
  - Recommended for personal MCP servers you want available everywhere
- **Project-level (Optional)**: `./.claude/mcp.json` or `./.mcp.json`
  - Can override or add to global servers for specific projects
  - Less common; most users configure globally

**Note**: Project-level **permissions** (allowing/denying MCP tools) are configured separately in `./.claude/settings.local.json`

## Current Setup

### Groq MCP Server

We use a Node.js-based Groq MCP server for LLM inference capabilities.

**Configuration Example:**

```json
{
  "mcpServers": {
    "groq": {
      "command": "node",
      "args": [
        "/Users/YOUR_USERNAME/.claude/mcp-groq.js"
      ],
      "env": {
        "GROQ_API_KEY": "your-groq-api-key-here"
      }
    }
  }
}
```

**Note**: On some systems (especially macOS with Homebrew), you may need to use the full path to node:
```json
"command": "/opt/homebrew/bin/node"
```

To find your node path, run: `which node`

## Setup Instructions

### 1. Obtain the MCP Server Script

Ensure you have the `mcp-groq.js` file in your `~/.claude/` directory.

### 2. Get Your API Key

- Sign up at [Groq Cloud](https://console.groq.com/)
- Generate an API key
- Store it securely (recommended: use environment variables)

### 3. Configure the MCP Server

**Option A: User-level (Recommended for personal use)**

Add the configuration to `~/.claude.json` under the `mcpServers` key:

```json
{
  "mcpServers": {
    "groq": {
      "command": "node",
      "args": [
        "/Users/YOUR_USERNAME/.claude/mcp-groq.js"
      ],
      "env": {
        "GROQ_API_KEY": "your-actual-api-key"
      }
    }
  }
}
```

**Option B: Project-level (For team collaboration)**

Create `.mcp.json` in your project root:

```json
{
  "groq": {
    "command": "node",
    "args": [
      "${HOME}/.claude/mcp-groq.js"
    ],
    "env": {
      "GROQ_API_KEY": "${GROQ_API_KEY}"
    }
  }
}
```

Then set the environment variable:
```bash
export GROQ_API_KEY="your-actual-api-key"
```

### 4. Verify Configuration

Start Claude Code in your project directory:
```bash
cd /path/to/your/project
claude
```

Then check MCP server status:
```
/mcp
```

This will show you all configured MCP servers and their connection status. You should see your Groq server listed with a ✔ connected indicator.

## Environment Variables

The `env` object supports variable expansion:
- `${HOME}` - User's home directory
- `${VARIABLE_NAME}` - Any environment variable

## Security Best Practices

1. **Never commit API keys** to version control
2. Use environment variables for sensitive data
3. Add `.mcp.json` to `.gitignore` if it contains secrets
4. Use `.mcp.json.example` to share configuration templates

## Troubleshooting

### Server Not Starting
- Check that Node.js is installed: `node --version`
- Verify the script path exists
- Check file permissions

### API Key Issues
- Ensure the API key is valid
- Check environment variable is set correctly
- Verify no extra whitespace in the key

### Connection Errors
- Check MCP server status with `/mcp` command
- Review Claude Code logs in `~/.claude/debug/` for detailed error messages
- Ensure the MCP server script has execute permissions
- Verify no firewall blocking local connections

## Additional MCP Servers

You can add multiple MCP servers:

```json
{
  "mcpServers": {
    "groq": {
      "command": "node",
      "args": ["/path/to/mcp-groq.js"],
      "env": {"GROQ_API_KEY": "${GROQ_API_KEY}"}
    },
    "another-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {}
    }
  }
}
```

## References

- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Groq Documentation](https://console.groq.com/docs)
