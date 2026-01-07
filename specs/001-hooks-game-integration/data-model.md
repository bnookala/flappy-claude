# Data Model: Flappy Claude

**Feature**: 001-hooks-game-integration
**Date**: 2026-01-06

## Entities

### Bird

The player-controlled character.

| Field | Type | Description |
|-------|------|-------------|
| y | float | Vertical position (0 = top of screen) |
| velocity | float | Current vertical velocity (positive = downward) |
| x | int | Horizontal position (fixed, typically 1/4 screen width) |

**Validation Rules**:
- `y` must be >= 0 and <= screen_height
- `velocity` bounded by terminal velocity constants

**State Transitions**:
- `flap()`: Sets velocity to negative (upward) flap strength
- `update()`: Applies gravity to velocity, updates y position

### Pipe

An obstacle the bird must navigate through.

| Field | Type | Description |
|-------|------|-------------|
| x | int | Horizontal position (moves leftward each frame) |
| gap_y | int | Y position of the center of the gap |
| gap_size | int | Height of the gap opening |
| passed | bool | Whether bird has passed this pipe (for scoring) |

**Validation Rules**:
- `gap_y` must allow gap to fit within screen bounds
- `gap_size` from config (typically 6-8 terminal rows)

**State Transitions**:
- `update()`: Decrements x by pipe speed
- `mark_passed()`: Sets passed = True when bird.x > pipe.x

### GameState

Overall game state container.

| Field | Type | Description |
|-------|------|-------------|
| bird | Bird | The player character |
| pipes | list[Pipe] | Active pipes on screen |
| score | int | Current score (pipes passed) |
| high_score | int | Best score from file |
| status | GameStatus | Current game phase |
| mode | GameMode | Auto-restart or single-life |
| claude_ready | bool | Whether Claude has finished (from signal file) |

**GameStatus Enum**:
- `PLAYING`: Active gameplay
- `DEAD`: Collision occurred, showing score (brief in auto-restart)
- `PROMPTED`: Showing "Claude is ready" prompt
- `EXITING`: User chose to exit

**GameMode Enum**:
- `AUTO_RESTART`: Default - restart after death
- `SINGLE_LIFE`: Exit after death

### Config

Game configuration constants.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| gravity | float | 0.5 | Downward acceleration per frame |
| flap_strength | float | -2.0 | Upward velocity on flap |
| pipe_speed | int | 1 | Horizontal pixels per frame |
| pipe_gap | int | 7 | Gap height in rows |
| pipe_spacing | int | 25 | Horizontal distance between pipes |
| fps | int | 30 | Target frames per second |
| death_display_time | float | 1.0 | Seconds to show score after death |

### HighScoreFile

Persistent high score storage.

| Field | Type | Description |
|-------|------|-------------|
| score | int | Best score achieved |

**File Location**: `~/.flappy-claude/highscore`
**Format**: Plain text integer

**Validation**:
- If file missing/corrupted: treat as 0
- Create parent directory if needed

### SignalFile

IPC mechanism for hook communication.

| Field | Type | Description |
|-------|------|-------------|
| exists | bool | Whether file exists |
| content | str | "ready" when Claude finished |

**File Location**: `/tmp/flappy-claude-signal`

**State Transitions**:
- PreToolUse hook: Creates empty file (game running indicator)
- Stop hook: Writes "ready" to file
- Game: Polls for "ready", shows prompt
- Game exit: Deletes file

## Relationships

```
GameState
├── Bird (1:1) - owns player character
├── Pipes (1:N) - owns active obstacles
├── Config (reference) - uses shared config
├── HighScoreFile (1:1) - reads/writes high score
└── SignalFile (1:1) - polls for Claude status
```

## File System Layout

```
~/.flappy-claude/
└── highscore              # Persistent high score (plain integer)

/tmp/
└── flappy-claude-signal   # IPC signal file (transient)
```
