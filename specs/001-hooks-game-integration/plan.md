# Implementation Plan: Claude Code Hooks Game Integration

**Branch**: `001-hooks-game-integration` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-hooks-game-integration/spec.md`

## Summary

Integrate Flappy Claude game with Claude Code hooks to provide entertainment during wait times. When Claude executes tools, users are offered to play a terminal-based Flappy Bird game. The game uses signal files for inter-process communication, supports configurable game-over behavior (auto-restart or single-life), and persists high scores locally.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: rich (terminal rendering), pytest (dev)
**Storage**: File-based (~/.flappy-claude/highscore for scores, /tmp/flappy-claude-signal for IPC)
**Testing**: pytest for core game logic (collision, physics, scoring)
**Target Platform**: macOS, Linux (terminals with ANSI support)
**Project Type**: Single project (Python package)
**Performance Goals**: 30 fps terminal refresh, <2s game startup, <1s signal response
**Constraints**: Minimal dependencies (rich only), offline-capable, single `uvx` command launch
**Scale/Scope**: Single-player terminal game, ~300-500 lines core implementation

**Research Outcome** (see [research.md](./research.md)):
- Rich chosen over curses (simpler API, better Unicode/emoji) and Textual (overkill)
- Rich's `Live` display with `refresh_per_second=30` for game loop
- Raw stdin with `select` for non-blocking keyboard input (no extra dependency)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Zero-Install Playability | ✅ PASS | Game launches via `uvx flappy-claude`; rich is pure Python, installs fast; no external assets |
| II. Simplicity-First | ✅ PASS | Using rich (simpler than curses); single package structure; <500 lines target; no premature abstractions |
| III. Core Logic Testing | ✅ PASS | Unit tests planned for collision detection, gravity/physics, score calculation |

**Gate Result**: PASS - All constitution principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-hooks-game-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface spec)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
flappy_claude/
├── __init__.py          # Package init with version
├── __main__.py          # Entry point for `python -m flappy_claude`
├── game.py              # Core game loop, rendering with Rich Live
├── physics.py           # Gravity, collision detection, movement (testable)
├── entities.py          # Bird, Pipe, GameState dataclasses
├── config.py            # Game configuration (speeds, dimensions, modes)
├── input.py             # Non-blocking keyboard input (select-based)
├── ipc.py               # Signal file handling for hook communication
└── scores.py            # High score persistence (testable)

hooks/
├── pretooluse.sh        # PreToolUse hook - prompts user, launches game
└── stop.sh              # Stop hook - signals game that Claude is ready

tests/
├── test_physics.py      # Collision, gravity tests
├── test_scores.py       # High score persistence tests
└── test_entities.py     # Entity state transition tests

pyproject.toml           # Package config with uvx entry point
```

**Structure Decision**: Single Python package with modular files for testability. Rich handles rendering via `Live` display. Hook scripts are shell-based per Claude Code hook requirements. Tests cover core logic only (per constitution).

## Complexity Tracking

> No violations - design follows constitution principles.

| Aspect | Decision | Justification |
|--------|----------|---------------|
| Rich vs curses vs Textual | Rich | Simpler API than curses, lighter than Textual; see research.md |
| Modular files vs single file | Multiple files | Enables targeted unit testing per constitution principle III |
| Shell hooks vs Python hooks | Shell scripts | Claude Code hooks require shell commands; keeps game pure Python |
| Extra keyboard library vs raw stdin | Raw stdin | Avoids dependency; select-based approach works on macOS/Linux |
