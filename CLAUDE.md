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
- **Terminal UI**: curses (standard library) or blessed
- **Testing**: pytest
- **Build**: pyproject.toml with hatchling

## Core Principles (from Constitution)

1. **Zero-Install Playability**: Game MUST run with `uvx flappy-claude` - no setup required
2. **Simplicity-First**: No premature abstractions; single-file is fine if <500 lines
3. **Core Logic Testing**: Unit tests required for physics, collision, scoring; NOT for rendering/input

## Project Structure

```
flappy_claude/           # Main package (to be created)
  __init__.py
  __main__.py           # Entry point for `python -m flappy_claude`
  game.py               # Core game logic
tests/                  # pytest tests for game logic
pyproject.toml          # Package configuration with uvx entry point
.specify/               # SpecKit scaffolding
  memory/constitution.md
```

## SpecKit Workflow

Available skills for feature development:

- `/speckit.specify` - Create feature specifications
- `/speckit.plan` - Generate implementation plans
- `/speckit.tasks` - Generate task lists
- `/speckit.implement` - Execute tasks

## Tickets

This project uses a CLI ticket system for task management. Run `tk help` when you need to use it.
