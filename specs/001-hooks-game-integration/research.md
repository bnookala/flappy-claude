# Research: Terminal Rendering Libraries for Flappy Claude

**Date**: 2026-01-06
**Feature**: 001-hooks-game-integration

## Decision Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Terminal Rendering | **Rich** with `Live` display | Balance of simplicity, zero-install friendliness, and sufficient game loop support |
| Keyboard Input | `pynput` or raw stdin with `select` | Rich doesn't handle input; need lightweight complement |
| Game Loop | `Live(refresh_per_second=30)` + update loop | 30fps sufficient for terminal game; matches typical refresh capability |

---

## Research Area 1: Terminal Rendering Library

### Option A: curses (stdlib)

**Pros**:
- Zero dependencies (standard library)
- Fast, low-level control
- Battle-tested for terminal games

**Cons**:
- Complex, low-level API
- Platform-specific quirks (macOS vs Linux differences)
- Poor Unicode/emoji support out of the box
- Manual color management

### Option B: Rich

**Pros**:
- Beautiful text rendering with colors, styles, emoji
- `Live` display with configurable `refresh_per_second` (can set to 60fps)
- Simple API: wrap content in `Live()` context, update in loop
- Lightweight dependency (~30 files, pure Python)
- Handles terminal resize automatically

**Cons**:
- Not designed for games (but can work)
- Default refresh is only 4fps (must override)
- No built-in keyboard input handling
- Fullscreen layout model

**Game Loop Pattern**:
```python
from rich.live import Live
from rich.text import Text

with Live(render_game(), refresh_per_second=30) as live:
    while running:
        update_game_state()
        live.update(render_game())
```

### Option C: Textual

**Pros**:
- Full application framework with `set_interval` for game ticks
- Built-in keyboard event handling (`on_key`)
- Has 60fps animation example in docs
- Line API for custom widget rendering
- Async-native design

**Cons**:
- Heavy dependency (full framework)
- Overkill for simple game
- Windows has 15ms timer granularity issue
- Steeper learning curve
- More complex setup for simple use case

**Game Loop Pattern**:
```python
class FlappyApp(App):
    def on_mount(self):
        self.set_interval(1/30, self.game_tick)

    def game_tick(self):
        self.update_state()
        self.refresh()

    def on_key(self, event):
        if event.key == "space":
            self.flap()
```

### Decision: Rich

**Rationale**:
1. **Simplicity-First (Constitution II)**: Rich is lighter than Textual while being much easier than curses
2. **Zero-Install Playability (Constitution I)**: Rich is a single pure-Python package, installs quickly via uvx
3. **Sufficient for purpose**: 30fps `Live` refresh is adequate for terminal game
4. **Beautiful output**: Rich's text styling makes the game visually appealing with minimal effort

**Trade-off**: Need separate solution for keyboard input (Rich doesn't handle it)

---

## Research Area 2: Keyboard Input

### Challenge
Rich's `Live` display doesn't provide keyboard input handling. Need a way to capture spacebar presses without blocking the game loop.

### Option A: pynput

**Pros**: Cross-platform, non-blocking, well-maintained
**Cons**: Extra dependency, requires accessibility permissions on macOS

### Option B: Raw stdin with select (Unix)

**Pros**: No extra dependency, works on macOS/Linux
**Cons**: Platform-specific, more complex code

### Option C: Simple blocking input in separate thread

**Pros**: Simple to implement
**Cons**: Threading complexity, potential race conditions

### Decision: Raw stdin with select + fallback

**Rationale**:
- Avoid extra dependencies (Constitution I & II)
- Target platforms are macOS/Linux only (per spec assumptions)
- Pattern is well-established for terminal games

**Implementation Pattern**:
```python
import sys
import select
import tty
import termios

def get_key_nonblocking():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None
```

---

## Research Area 3: Inter-Process Communication (Hooks ↔ Game)

### Mechanism: Signal File

Per clarification session, using signal file for hook-to-game communication.

**Implementation**:
- PreToolUse hook: Launches game, stores PID in signal file
- Stop hook: Writes "ready" to signal file
- Game: Polls signal file every frame, shows prompt when "ready" detected

**File Location**: `/tmp/flappy-claude-{session_id}` or `~/.flappy-claude/signal`

**Polling Strategy**: Check file modification time or existence, not content read (faster)

---

## Research Area 4: Claude Code Hooks Integration

### Hook Data Format

Hooks receive JSON via stdin with tool information:
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "ls -la"}
}
```

### PreToolUse Hook Script Pattern

```bash
#!/bin/bash
# Read JSON input (not used for game prompt, but available)
read -t 0.1 json_input

# Check if game already running
if [ -f /tmp/flappy-claude-signal ]; then
    exit 0  # Don't prompt again
fi

# Prompt user (with timeout for non-blocking check)
echo -n "Would you like to play Flappy Claude? (y)es/(n)o: "
read -t 0.5 -n 1 response

if [[ "$response" =~ ^[Yy]$ ]]; then
    # Launch game in background
    uvx flappy-claude &
fi
```

### Stop Hook Script Pattern

```bash
#!/bin/bash
# Signal game that Claude is ready
echo "ready" > /tmp/flappy-claude-signal
```

---

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Textual | Overkill for simple game; heavier dependency |
| curses | More complex API; poor Unicode support |
| pygame | Not terminal-based; graphical window |
| blessed | Similar to curses but less maintained |

---

## References

- [Rich Live Display Documentation](https://rich.readthedocs.io/en/latest/live.html)
- [Textual Animation Guide](https://textual.textualize.io/guide/animation/)
- [Textual Tutorial](https://textual.textualize.io/tutorial/)
- [Python Rich Live Asynchronous Pattern](https://epsi.bitbucket.io/monitor/2022/12/05/python-rich-live-03/)
- [Terminal Flappy Bird Example](https://github.com/SkwalExe/flappy)
- [Claude Code Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks)
