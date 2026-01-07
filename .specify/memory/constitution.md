<!--
Sync Impact Report
==================
- Version change: N/A → 1.0.0 (initial constitution)
- Added principles:
  - I. Zero-Install Playability
  - II. Simplicity-First
  - III. Core Logic Testing
- Added sections:
  - Technical Stack
  - Development Workflow
- Removed sections: None (initial creation)
- Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ No updates needed (generic template)
  - .specify/templates/spec-template.md: ✅ No updates needed (generic template)
  - .specify/templates/tasks-template.md: ✅ No updates needed (generic template)
- Follow-up TODOs: None
==================
-->

# Flappy Claude Constitution

## Core Principles

### I. Zero-Install Playability

The game MUST be runnable with a single command via `uvx` without any prior installation or setup.

- Package MUST be published to PyPI or runnable from a GitHub URL
- All dependencies MUST be declared in `pyproject.toml`
- Entry point MUST be a single CLI command (e.g., `uvx flappy-claude`)
- No external assets requiring separate downloads
- Game MUST work offline after initial package fetch

### II. Simplicity-First

Every feature and abstraction MUST justify its existence. Start with the minimum viable game loop.

- Prefer standard library over external dependencies where reasonable
- No premature abstractions—add complexity only when needed
- Single-file implementation is acceptable if it stays readable (<500 lines)
- Split into modules only when a file exceeds readability threshold
- YAGNI: Do not build features "for later"

### III. Core Logic Testing

Game physics and scoring logic MUST have unit tests. UI/rendering is tested manually.

- Unit tests MUST cover: collision detection, gravity/physics, score calculation
- Unit tests are NOT required for: rendering, input handling, sound
- Tests run via `pytest` or `uv run pytest`
- New game logic MUST include corresponding tests before merge

## Technical Stack

- **Language**: Python 3.11+
- **Package Manager**: uv (with uvx for zero-install execution)
- **CLI Framework**: Standard library `curses` for terminal rendering (or `blessed` if curses insufficient)
- **Testing**: pytest
- **Build**: pyproject.toml with hatchling or setuptools backend
- **Distribution**: PyPI

## Development Workflow

1. Run locally during development: `uv run python -m flappy_claude`
2. Run tests: `uv run pytest`
3. Test zero-install experience: `uvx .` (from project root)
4. Publish: `uv build && uv publish`

## Governance

This constitution defines the non-negotiable constraints for the Flappy Claude project.

- All code changes MUST comply with these principles
- Amendments require explicit justification and version increment
- Use CLAUDE.md for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-06
