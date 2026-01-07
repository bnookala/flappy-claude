# CLI Contract: Flappy Claude

**Feature**: 001-hooks-game-integration
**Date**: 2026-01-06

## Game Entry Point

### Command

```bash
uvx flappy-claude [OPTIONS]
```

Or during development:
```bash
uv run python -m flappy_claude [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--single-life` | `-s` | flag | false | Exit after first death instead of auto-restart |
| `--signal-file` | | path | `/tmp/flappy-claude-signal` | Path to IPC signal file |
| `--help` | `-h` | flag | | Show help and exit |
| `--version` | `-V` | flag | | Show version and exit |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Normal exit (user quit or returned to Claude) |
| 1 | Error (terminal not supported, file error, etc.) |

### Examples

```bash
# Standard launch (auto-restart mode)
uvx flappy-claude

# Single-life mode
uvx flappy-claude --single-life

# Custom signal file (for testing)
uvx flappy-claude --signal-file /tmp/test-signal
```

---

## Hook Scripts Contract

### PreToolUse Hook

**Purpose**: Prompt user to play game during Claude tool execution.

**Trigger**: Claude Code PreToolUse event

**Input** (stdin): JSON with tool information (not used)

**Behavior**:
1. Check if signal file exists (game already running) → exit silently
2. Print prompt: `"Would you like to play Flappy Claude? (y)es/(n)o: "`
3. Read single character with short timeout
4. If 'y'/'Y': Launch `uvx flappy-claude &` in background
5. If 'n'/'N' or timeout: Exit silently

**Output**: None (game launches in background)

**Exit Codes**:
- 0: Always (don't block Claude)

### Stop Hook

**Purpose**: Signal game that Claude has finished.

**Trigger**: Claude Code Stop event

**Input** (stdin): JSON (not used)

**Behavior**:
1. Write "ready" to signal file
2. Exit

**Output**: None

**Exit Codes**:
- 0: Always

---

## Keyboard Controls (In-Game)

| Key | Action |
|-----|--------|
| `Space` | Flap (move bird upward) |
| `q` | Quit game |
| `Ctrl+C` | Quit game |
| `y` | Accept prompt (return to Claude / play again) |
| `n` | Decline prompt (continue playing / stay) |

---

## Display Contract

### Game Screen Layout

```
┌────────────────────────────────────────┐
│ Score: 42          High: 128    🎮     │
│                                        │
│                    ████                │
│                    ████                │
│        🐦                              │
│                    ████                │
│                    ████                │
│                                        │
│────────────────────────────────────────│
│ SPACE to flap | Q to quit              │
└────────────────────────────────────────┘
```

### Claude Ready Prompt (Overlay)

```
┌────────────────────────────────────────┐
│                                        │
│   ┌──────────────────────────────┐     │
│   │  Claude is ready!            │     │
│   │  Return to session? (y/n)    │     │
│   └──────────────────────────────┘     │
│                                        │
└────────────────────────────────────────┘
```

### Death Screen (Auto-restart mode)

```
┌────────────────────────────────────────┐
│                                        │
│          💀 Score: 42                  │
│          High Score: 128               │
│                                        │
│          Restarting...                 │
│                                        │
└────────────────────────────────────────┘
```

### Death Screen (Single-life mode)

```
┌────────────────────────────────────────┐
│                                        │
│          💀 Game Over!                 │
│          Score: 42                     │
│          High Score: 128               │
│                                        │
│          Press any key to exit         │
│                                        │
└────────────────────────────────────────┘
```
