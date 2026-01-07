# Quickstart: Flappy Claude Development

**Feature**: 001-hooks-game-integration
**Date**: 2026-01-06

## Prerequisites

- Python 3.11+
- uv package manager
- macOS or Linux terminal with ANSI support

## Setup

```bash
# Clone/navigate to repo
cd flappy-claude

# Create virtual environment and install deps
uv sync

# Verify installation
uv run python -m flappy_claude --help
```

## Development Commands

```bash
# Run game locally
uv run python -m flappy_claude

# Run in single-life mode
uv run python -m flappy_claude --single-life

# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_physics.py -v

# Test zero-install experience
uvx .
```

## Project Structure

```
flappy_claude/
├── __init__.py      # Version
├── __main__.py      # Entry point
├── game.py          # Main loop + Rich rendering
├── physics.py       # Collision, gravity (TESTABLE)
├── entities.py      # Bird, Pipe, GameState
├── config.py        # Constants
├── input.py         # Keyboard handling
├── ipc.py           # Signal file
└── scores.py        # High score (TESTABLE)

hooks/
├── pretooluse.sh    # Launch prompt
└── stop.sh          # Signal ready

tests/
├── test_physics.py
├── test_scores.py
└── test_entities.py
```

## Testing the Hook Integration

### Manual Test Flow

1. **Setup hooks** (one-time):
   ```bash
   # Add to ~/.claude/settings.json
   {
     "hooks": {
       "PreToolUse": [{
         "matcher": "*",
         "hooks": [{"type": "command", "command": "/path/to/hooks/pretooluse.sh"}]
       }],
       "Stop": [{
         "matcher": "*",
         "hooks": [{"type": "command", "command": "/path/to/hooks/stop.sh"}]
       }]
     }
   }
   ```

2. **Trigger a tool use** in Claude Code (e.g., run a bash command)

3. **Accept game prompt** when it appears

4. **Play game** until Claude finishes

5. **Verify return prompt** appears when Claude is ready

6. **Accept return** and verify back in Claude session

### Signal File Test

```bash
# Terminal 1: Start game
uv run python -m flappy_claude

# Terminal 2: Simulate Claude ready signal
echo "ready" > /tmp/flappy-claude-signal

# Verify: Game should show "Claude is ready" prompt
```

## Key Files to Implement

### 1. physics.py (Testable Core)

```python
def apply_gravity(bird: Bird, config: Config) -> Bird:
    """Apply gravity to bird, return updated bird."""

def check_collision(bird: Bird, pipes: list[Pipe], screen_height: int) -> bool:
    """Check if bird collides with pipes or boundaries."""

def check_pipe_passed(bird: Bird, pipe: Pipe) -> bool:
    """Check if bird has passed the pipe for scoring."""
```

### 2. scores.py (Testable)

```python
def load_high_score(path: Path) -> int:
    """Load high score from file, return 0 if missing/invalid."""

def save_high_score(path: Path, score: int) -> None:
    """Save high score to file, creating dirs if needed."""
```

### 3. game.py (Main Loop)

```python
def main():
    with Live(render_game(state), refresh_per_second=30) as live:
        while state.status != GameStatus.EXITING:
            handle_input(state)
            update_state(state)
            check_signal_file(state)
            live.update(render_game(state))
```

## Validation Checklist

Before PR:

- [ ] `uv run pytest` passes
- [ ] `uvx .` launches game successfully
- [ ] Game renders correctly in terminal
- [ ] Spacebar flap works
- [ ] Collision detection works
- [ ] Score increments on pipe pass
- [ ] High score persists across sessions
- [ ] Signal file triggers "Claude ready" prompt
- [ ] Game exits cleanly on 'q' or prompt acceptance
- [ ] Auto-restart works in default mode
- [ ] Single-life mode exits on death
