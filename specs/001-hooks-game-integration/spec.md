# Feature Specification: Claude Code Hooks Game Integration

**Feature Branch**: `001-hooks-game-integration`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Claude Code hooks integration for Flappy Claude game during wait times"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play Game While Claude Works (Priority: P1)

A user is working with Claude Code when Claude begins a long-running operation (tool execution, thinking). The user sees an option to play Flappy Claude while waiting. They accept, play the game, and when Claude finishes its work, they're prompted to return to their session.

**Why this priority**: This is the core value proposition - turning idle waiting time into entertainment. Without this flow working end-to-end, there's no product.

**Independent Test**: Can be fully tested by triggering a Claude Code tool use, accepting the game prompt, playing briefly, and then having Claude complete its work to see the return prompt.

**Acceptance Scenarios**:

1. **Given** Claude Code is executing a tool (e.g., Bash command), **When** the PreToolUse hook fires, **Then** the user sees "Would you like to play Flappy Claude? (y)es/(n)o" in their terminal.

2. **Given** the game prompt is displayed and user types "y" or "Y" or "yes" or "YES", **When** input is received before Claude completes, **Then** the Flappy Claude game launches via `uvx`.

3. **Given** the game prompt is displayed and user types "n" or "N" or "no" or "NO", **When** input is received, **Then** the prompt disappears and the user continues waiting normally.

4. **Given** the game prompt is displayed, **When** Claude completes its work before user responds, **Then** the prompt is dismissed and Claude's response appears normally.

---

### User Story 2 - Return to Claude Session (Priority: P2)

While the user is playing Flappy Claude, Claude finishes its work. The game pauses/overlays a prompt asking if the user wants to return to Claude. The user can choose to continue playing or return to their Claude session.

**Why this priority**: This is essential for the seamless experience - users must be able to transition back to work without losing context or having to manually manage processes.

**Independent Test**: Can be tested by launching the game directly, simulating a "Claude finished" signal, and verifying the return prompt appears and functions correctly.

**Acceptance Scenarios**:

1. **Given** the user is playing Flappy Claude and Claude finishes its work, **When** the Stop hook fires, **Then** the game displays "Claude is ready! Return to session? (y)es/(n)o" without closing the game.

2. **Given** the return prompt is displayed and user types "y" or "Y" or "yes", **When** input is received, **Then** the game exits gracefully and the user sees Claude's response.

3. **Given** the return prompt is displayed and user types "n" or "N" or "no", **When** input is received, **Then** the prompt dismisses and the user continues playing.

4. **Given** the user manually exits the game (e.g., 'q' key or Ctrl+C), **When** the game exits, **Then** the user returns to their Claude Code session with Claude's response visible.

---

### User Story 3 - Core Game Loop (Priority: P3)

The user plays a Flappy Bird-style terminal game where they control a character (Claude mascot) navigating through obstacles by pressing a key to "flap" upward against gravity.

**Why this priority**: While essential for entertainment value, the game mechanics are secondary to the hook integration. A minimal playable game is sufficient for MVP.

**Independent Test**: Can be tested by running `uvx flappy-claude` directly and verifying the game renders, responds to input, and tracks score.

**Acceptance Scenarios**:

1. **Given** the game is launched, **When** it starts, **Then** the user sees a terminal-based game screen with a character and obstacles.

2. **Given** the game is running, **When** the user presses the flap key (spacebar), **Then** the character moves upward.

3. **Given** the game is running in default mode, **When** the character collides with an obstacle or boundary, **Then** the score is displayed briefly and the game auto-restarts.

4. **Given** the game is running in single-life mode, **When** the character collides with an obstacle or boundary, **Then** the game ends and displays the final score.

5. **Given** the game is running, **When** the character passes an obstacle, **Then** the score increments.

6. **Given** a high score file exists, **When** the game displays the score, **Then** the current high score is also shown.

7. **Given** the player achieves a score higher than the stored high score, **When** the game ends or restarts, **Then** the new high score is persisted to file.

---

### Edge Cases

- What happens when multiple tool calls happen in rapid succession? The game prompt should only appear once per "waiting period" - if game is already running or prompt is showing, do not display another prompt.
- How does the system handle if the game crashes or fails to launch? Fall back to normal waiting behavior and log the error to stderr.
- What if the user's terminal doesn't support curses/terminal graphics? Display a friendly error message suggesting minimum terminal requirements.
- What happens if Claude finishes while the game is still initializing? Skip game launch entirely and proceed with normal Claude response flow.
- What if the user presses an invalid key at the prompt? Ignore invalid input and continue waiting for valid y/n response.
- What if the high score file is missing or corrupted? Initialize high score to 0 and create/overwrite the file on first score save.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide Claude Code hook configuration that triggers on PreToolUse events
- **FR-002**: System MUST display a non-blocking prompt asking if user wants to play during wait
- **FR-003**: System MUST accept case-insensitive y/yes/n/no responses to the game prompt
- **FR-004**: System MUST launch the game via `uvx flappy-claude` when user accepts
- **FR-005**: System MUST dismiss the prompt silently if Claude completes before user responds
- **FR-006**: System MUST signal the running game when Claude's work completes (via Stop hook)
- **FR-007**: Game MUST display an in-game prompt when signaled that Claude is ready
- **FR-008**: Game MUST allow user to choose to continue playing or exit when Claude is ready
- **FR-009**: Game MUST exit gracefully and return user to Claude session when user chooses to return
- **FR-010**: Game MUST provide a manual exit option (e.g., 'q' key) that returns to Claude session
- **FR-011**: Game MUST render in a standard terminal using text/ASCII graphics
- **FR-012**: Game MUST implement basic Flappy Bird mechanics: gravity, flap, obstacles, collision, scoring
- **FR-013**: Game MUST support configurable game-over behavior: auto-restart (default) or single-life mode
- **FR-014**: Game MUST persist high score to ~/.flappy-claude/highscore and display it during gameplay

### Key Entities

- **Game Session**: Represents an active instance of Flappy Claude, tracks score, game state (playing/paused/prompted), and polls signal file for hook communication
- **Hook Coordinator**: The shell script/process that manages the prompt display, user input capture, game launching, and writes to signal file when Claude completes
- **Game State**: Current state including player position, obstacles, score, and whether a "return to Claude" prompt is active
- **Signal File**: Temporary file used for hook-to-game communication; presence indicates Claude has finished work
- **High Score File**: Persistent file at ~/.flappy-claude/highscore storing the user's best score across sessions

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start playing the game within 2 seconds of accepting the prompt
- **SC-002**: The return-to-Claude prompt appears within 1 second of Claude finishing its work
- **SC-003**: Users can complete a full play-wait-return cycle without any manual process management
- **SC-004**: Game runs at a smooth, playable frame rate (minimum 15 fps equivalent for terminal updates)
- **SC-005**: 100% of game exits (voluntary or prompted) return user to their Claude session
- **SC-006**: Zero-install experience works: `uvx flappy-claude` launches the game with no prior setup

## Clarifications

### Session 2026-01-06

- Q: What inter-process communication mechanism should hooks use to signal the game? → A: Signal file - Hook writes a file, game polls for it
- Q: What should happen when the player dies (collision)? → A: Configurable - Default is auto-restart; single-life mode available as option
- Q: Should the game track high scores across sessions? → A: Local file - Store high score in ~/.flappy-claude/highscore

## Assumptions

- Users have a terminal that supports curses or basic ANSI escape sequences
- Users have `uv` installed (required for Claude Code usage anyway)
- The game process and hook scripts communicate via a signal file (hook writes, game polls)
- Users are on macOS or Linux (curses standard library support)
