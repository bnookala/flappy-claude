# Flappy Claude

A terminal-based Flappy Bird game that integrates with Claude Code hooks to provide entertainment during wait times.

## Quick Start

```bash
uvx flappy-claude
```

## Controls

- `SPACE` - Flap / Resume from pause
- `Y` - Return to Claude (when Claude is waiting)
- `Q` / `ESC` - Quit

## Claude Code Integration

Flappy Claude integrates with Claude Code hooks to automatically:
- **Prompt to play** when Claude is working on a long task
- **Pause the game** when Claude asks you a question
- **Notify you** when Claude finishes and is ready for input

### How It Works

1. **PreToolUse Hook**: Monitors Claude's tool usage. After several tool calls in a conversation turn, prompts you to play while Claude works.
2. **Stop Hook**: Fires when Claude finishes a response. Signals the game that Claude is ready, showing a prompt to return.
3. **Pause on Question**: When Claude uses `AskUserQuestion`, the game pauses with a 4-second cooldown so you can switch to answer Claude.

### Installation

#### Option 1: Claude Code Plugin (Recommended)

Install as a Claude Code plugin for automatic hook configuration:

```bash
# Add the marketplace (if using a custom marketplace)
/plugin marketplace add yourusername/flappy-claude

# Install the plugin
/plugin install flappy-claude
```

Or install directly from GitHub:

```bash
/plugin install github:yourusername/flappy-claude
```

That's it! The hooks are automatically configured.

#### Option 2: Manual Installation

If you prefer manual setup:

1. **Copy the hook scripts** to your Claude Code hooks directory:

   ```bash
   mkdir -p ~/.claude/hooks
   curl -o ~/.claude/hooks/pretooluse.sh https://raw.githubusercontent.com/yourusername/flappy-claude/main/hooks/pretooluse.sh
   curl -o ~/.claude/hooks/stop.sh https://raw.githubusercontent.com/yourusername/flappy-claude/main/hooks/stop.sh
   chmod +x ~/.claude/hooks/*.sh
   ```

2. **Configure Claude Code** by adding hooks to your settings file.

   Edit `~/.claude/settings.json` (create if it doesn't exist):

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "*",
           "hooks": ["~/.claude/hooks/pretooluse.sh"]
         }
       ],
       "Stop": [
         {
           "matcher": "*",
           "hooks": ["~/.claude/hooks/stop.sh"]
         }
       ]
     }
   }
   ```

The game runs via `uvx flappy-claude` - no Python installation required!

### Hook Behavior

#### PreToolUse Hook (`pretooluse.sh`)

Triggers during Claude's tool execution with the following conditions:
- Only prompts once every **10 conversation turns**
- Requires at least **5 tool calls** in the current turn before prompting
- Only prompts when a **terminal app is in focus** (macOS)
- **Pauses the game immediately** when Claude asks a question (`AskUserQuestion` tool)

Configuration variables at the top of `pretooluse.sh`:
```bash
TURNS_BETWEEN_PROMPTS=10    # Conversation turns between play prompts
MIN_TOOL_CALLS=5            # Minimum tool calls before prompting
```

#### Stop Hook (`stop.sh`)

Triggers when Claude finishes a response:
- Writes "ready" signal if game is running
- Game shows prompt: "Claude has finished! [Y] Return to Claude [N] Keep playing"
- Auto-closes after 10 seconds if no input

### Game States

| State | Description | Controls |
|-------|-------------|----------|
| **Waiting** | Start screen before playing | `SPACE` to start |
| **Playing** | Active gameplay | `SPACE` to flap, `Q` to quit |
| **Paused** | Claude asked a question | Wait 4s, then `SPACE` to resume |
| **Prompted** | Claude finished working | `Y` to return, `N` to keep playing |
| **Claude Waiting** | Playing after dismissing prompt | Header shows "CLAUDE WAITING", `Y` to return |

### File Locations

| File | Purpose |
|------|---------|
| `/tmp/flappy-claude-signal` | IPC signal file ("ready" or "pause") |
| `/tmp/flappy-claude-lock` | Lock directory (indicates game is running) |
| `/tmp/flappy-claude-hook.log` | Debug log for hook activity |
| `~/.flappy-claude/highscore` | Persistent high score |

### Troubleshooting

**Game doesn't pause when Claude asks a question:**
- Ensure the game was started after the hook updates (restart the game)
- Check that the lock directory exists: `ls -la /tmp/flappy-claude-lock`
- Check the hook log: `tail -f /tmp/flappy-claude-hook.log`

**Prompt to play never appears:**
- Verify hooks are installed: `ls ~/.claude/hooks/`
- Check Claude Code settings include the hooks configuration
- Ensure terminal is in focus (hook checks frontmost app on macOS)
- May need to wait for 5+ tool calls and 10+ conversation turns

**Game doesn't detect Claude is ready:**
- Check signal file: `cat /tmp/flappy-claude-signal`
- Verify stop hook is configured in settings.json

## Development

```bash
# Run locally
uv run python -m flappy_claude

# Run tests
uv run pytest

# Single-life mode (exit on death instead of auto-restart)
uv run python -m flappy_claude --single-life

# Custom signal file location
uv run python -m flappy_claude --signal-file /tmp/my-signal
```

## License

MIT
