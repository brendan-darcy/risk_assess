# Groq Integration

Two ways to use Groq API via the MCP server: slash command for one-off requests, and custom agent for continuous Groq-powered conversations.

## Installation

Two components have been installed:

1. **Slash Command**: `~/.claude/commands/groq.md` (for one-off requests)
2. **Custom Agent**: `~/.claude/agents/groq.md` (for continuous Groq mode)

## Usage

### Method 1: Groq Mode (Context-Based Model Switching)

Tell Claude to enter "Groq mode" and it will automatically route all subsequent questions through Groq:

```
Enter Groq mode - answer all my questions using Groq from now on until i say otherwise
```

Then just chat normally:
```
What is the capital of France?
Explain quantum computing
Write a Python function for fibonacci
```

To exit: `Exit Groq mode` or `Switch back to Claude`

**Note:** This works within a single conversation session and is limited by context window.

### Method 2: Slash Command (For One-Off Requests)

Use `/groq` for single requests:

```
/groq What is the capital of France?
```

With specific model:
```
/groq "Explain quantum computing" llama-3.1-70b-versatile
```

## Available Models

Popular Groq models you can use:
- `llama-3.1-70b-versatile` - Llama 3.1 70B (default)
- `mixtral-8x7b-32768` - Mixtral 8x7B
- `gemma2-9b-it` - Gemma 2 9B
- `llama-3.2-90b-text-preview` - Llama 3.2 90B

Default model: `llama-3.1-70b-versatile`

## How It Works

1. You type `/groq <your prompt>`
2. Claude receives the slash command
3. Claude uses the `groq.chat` MCP tool to send your prompt to Groq
4. Groq processes the request and returns the response
5. Claude displays the result to you

## Examples

### Simple Question
```
/groq What are the benefits of using MCP servers?
```

### Code Generation
```
/groq Write a Python function to calculate fibonacci numbers
```

### With Different Model
```
/groq "Explain machine learning" mixtral-8x7b-32768
```

## Editing the Command

To customize the slash command:
```bash
code ~/.claude/commands/groq.md
```

Or:
```bash
nano ~/.claude/commands/groq.md
```

## Comparison of Methods

**Groq Mode (context-based) - Best for extended use:**
- ✅ Works like model switching within a session
- ✅ All prompts automatically use Groq after activation
- ✅ Natural conversation flow
- ✅ No need to prefix every message
- ⚠️ Limited to current conversation context
- Use when: You want to have a full conversation with Groq

**Slash Command (/groq) - Best for one-off:**
- ✅ Quick single requests
- ✅ Explicit control
- ❌ Must use for each prompt
- Use when: You just need one Groq response

**Direct Tool Use (let Claude decide):**
- ✅ Most flexible
- ✅ Claude decides when appropriate
- ✅ Can combine with other operations
- Use when: You want Claude to intelligently choose when to use Groq

## Troubleshooting

### Groq Mode Not Working (Keeps Reverting to Claude)

Groq mode requires the `mcp__groq__groq_chat` tool to be approved. If not approved, the tool calls fail and responses revert to Claude.

**Fix:** Create or update `.claude/settings.local.json` in your project root:
```json
{
  "permissions": {
    "allow": [
      "mcp__groq__groq_chat"
    ],
    "deny": [],
    "ask": []
  }
}
```

Settings take effect immediately - no restart needed!

Alternatively, when Claude prompts for permission to use the Groq tool, you can:
1. Approve it for this session only, or
2. Approve it and save the permission to your project settings

**Note**: `.claude/settings.local.json` should be added to `.gitignore` to avoid committing it to version control.

### Command Not Found
Restart Claude Code to pick up the new slash command:
```bash
# Exit and restart
exit
claude
```

### MCP Server Not Connected
Check MCP status:
```
/mcp
```

Ensure groq server shows ✔ connected.

### API Errors
Check your GROQ_API_KEY environment variable:
```bash
echo $GROQ_API_KEY
```

## Quick Start

**For model-like switching behavior:**
```
Enter Groq mode - answer all my questions using Groq from now on until i say otherwise

> What is machine learning?
> How do neural networks work?
> Explain transformers
```

**For one-off requests:**
```
/groq What is the capital of France?
```

## Related Files

- MCP Server Script: `~/.claude/mcp-groq.js`
- MCP Configuration: `~/.claude.json` (mcpServers section)
- Slash Command: `~/.claude/commands/groq.md`
- Custom Agent: `~/.claude/agents/groq.md`
