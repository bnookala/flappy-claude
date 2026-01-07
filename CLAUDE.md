# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flappy Claude - a CLI-based Flappy Bird-style game built in Python, designed to run instantly via `uvx flappy-claude` with zero installation.

## Development Commands

```bash
# Run locally during development
uv run python -m flappy_claude

# Run tests
uv run pytest

# Test zero-install experience (from project root)
uvx .

# Build and publish
uv build && uv publish
```

## Architecture

- **Language**: Python 3.11+
- **Package Manager**: uv (with uvx for zero-install execution)
- **Terminal UI**: Rich library (Live display at 30fps)
- **Testing**: pytest
- **Build**: pyproject.toml with hatchling

## Core Principles (from Constitution)

1. **Zero-Install Playability**: Game MUST run with `uvx flappy-claude` - no setup required
2. **Simplicity-First**: No premature abstractions; single-file is fine if <500 lines
3. **Core Logic Testing**: Unit tests required for physics, collision, scoring; NOT for rendering/input

## Project Structure

```
flappy_claude/           # Main package
  __init__.py           # Version string
  __main__.py           # CLI entry point with argparse
  config.py             # Game configuration dataclass
  entities.py           # Bird, Pipe, GameState dataclasses
  physics.py            # Testable physics/collision/scoring
  input.py              # Non-blocking keyboard input
  game.py               # Rich rendering and game loop
  ipc.py                # Signal file IPC for Claude integration
  scores.py             # High score persistence
tests/                  # pytest tests for game logic
hooks/                  # Claude Code hook scripts
  pretooluse.sh         # Prompts user to play during tool use
  stop.sh               # Signals game when Claude is done
pyproject.toml          # Package configuration with uvx entry point
.specify/               # SpecKit scaffolding
```

## Claude Code Hook Installation

To use Flappy Claude with Claude Code hooks:

1. Copy hooks to your Claude Code hooks directory:
   ```bash
   mkdir -p ~/.claude/hooks
   cp hooks/pretooluse.sh ~/.claude/hooks/
   cp hooks/stop.sh ~/.claude/hooks/
   chmod +x ~/.claude/hooks/*.sh
   ```

2. Configure hooks in Claude Code settings (`.claude/settings.json`):
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

3. When Claude executes a tool, you'll be prompted to play. When Claude finishes, the game will show a "Claude is ready" prompt.

## SpecKit Workflow

Available skills for feature development:

- `/speckit.specify` - Create feature specifications
- `/speckit.plan` - Generate implementation plans
- `/speckit.tasks` - Generate task lists
- `/speckit.implement` - Execute tasks

## Tickets

This project uses a CLI ticket system for task management. Run `tk help` when you need to use it.

## Active Technologies
- Python 3.11+ + rich (terminal rendering), pytest (dev) (001-hooks-game-integration)
- File-based (~/.flappy-claude/highscore for scores, /tmp/flappy-claude-signal for IPC) (001-hooks-game-integration)

## Recent Changes
- 001-hooks-game-integration: Added Python 3.11+ + rich (terminal rendering), pytest (dev)
