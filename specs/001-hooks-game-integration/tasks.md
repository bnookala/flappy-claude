# Tasks: Claude Code Hooks Game Integration

**Input**: Design documents from `specs/001-hooks-game-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required per Constitution Principle III (Core Logic Testing) - physics, collision, scoring must have unit tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `flappy_claude/`, `tests/`, `hooks/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Python package structure

- [x] T001 Create pyproject.toml with hatchling build, rich dependency, pytest dev dependency, and uvx entry point in pyproject.toml
- [x] T002 [P] Create package directory structure: flappy_claude/, tests/, hooks/
- [x] T003 [P] Create flappy_claude/__init__.py with version string
- [x] T004 [P] Create empty flappy_claude/__main__.py with placeholder main()

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Config dataclass with game constants (gravity, flap_strength, pipe_speed, pipe_gap, fps, etc.) in flappy_claude/config.py
- [x] T006 [P] Create GameStatus and GameMode enums in flappy_claude/entities.py
- [x] T007 [P] Create Bird dataclass with y, velocity, x fields in flappy_claude/entities.py
- [x] T008 [P] Create Pipe dataclass with x, gap_y, gap_size, passed fields in flappy_claude/entities.py
- [x] T009 Create GameState dataclass referencing Bird, Pipe list, score, high_score, status, mode, claude_ready in flappy_claude/entities.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Play Game While Claude Works (Priority: P1) 🎯 MVP

**Goal**: When Claude executes a tool, user sees prompt to play game. If they accept, game launches via uvx and runs.

**Independent Test**: Trigger Claude Code tool use, accept game prompt, verify game launches and renders.

### Tests for User Story 1

- [x] T010 [P] [US1] Create test_physics.py with test for apply_gravity() function in tests/test_physics.py
- [x] T011 [P] [US1] Add test for check_collision() with bird hitting top/bottom boundaries in tests/test_physics.py
- [x] T012 [P] [US1] Add test for check_collision() with bird hitting pipe in tests/test_physics.py
- [x] T013 [P] [US1] Add test for check_pipe_passed() scoring logic in tests/test_physics.py

### Implementation for User Story 1

- [x] T014 [P] [US1] Implement apply_gravity(bird, config) function in flappy_claude/physics.py
- [x] T015 [P] [US1] Implement check_collision(bird, pipes, screen_height) function in flappy_claude/physics.py
- [x] T016 [P] [US1] Implement check_pipe_passed(bird, pipe) function in flappy_claude/physics.py
- [x] T017 [US1] Implement get_key_nonblocking() using select and stdin in flappy_claude/input.py
- [x] T018 [US1] Implement render_game(state) function returning Rich renderable in flappy_claude/game.py
- [x] T019 [US1] Implement game loop with Rich Live display (30fps) in flappy_claude/game.py
- [x] T020 [US1] Implement CLI argument parsing (--single-life, --signal-file, --help, --version) in flappy_claude/__main__.py
- [x] T021 [US1] Implement main() entry point that initializes GameState and runs game loop in flappy_claude/__main__.py
- [x] T022 [US1] Create pretooluse.sh hook script that prompts user and launches uvx flappy-claude in hooks/pretooluse.sh
- [x] T023 [US1] Verify game launches via `uv run python -m flappy_claude` and responds to spacebar input

**Checkpoint**: User Story 1 complete - game is playable and can be launched from hook prompt

---

## Phase 4: User Story 2 - Return to Claude Session (Priority: P2)

**Goal**: When Claude finishes work, game shows overlay prompt. User can return to Claude or continue playing.

**Independent Test**: Launch game, write "ready" to signal file, verify return prompt appears and y/n works.

### Implementation for User Story 2

- [x] T024 [P] [US2] Implement check_signal_file(path) function that polls for "ready" content in flappy_claude/ipc.py
- [x] T025 [P] [US2] Implement delete_signal_file(path) function for cleanup in flappy_claude/ipc.py
- [x] T026 [US2] Create stop.sh hook script that writes "ready" to signal file in hooks/stop.sh
- [x] T027 [US2] Add signal file polling to game loop (check each frame) in flappy_claude/game.py
- [x] T028 [US2] Implement render_claude_ready_prompt() overlay renderable in flappy_claude/game.py
- [x] T029 [US2] Add PROMPTED state handling: show overlay, process y/n input, exit or continue in flappy_claude/game.py
- [x] T030 [US2] Ensure clean exit deletes signal file and restores terminal in flappy_claude/game.py
- [x] T031 [US2] Test signal file integration: launch game, touch signal file, verify prompt appears

**Checkpoint**: User Story 2 complete - game responds to Claude completion signal

---

## Phase 5: User Story 3 - Core Game Loop (Priority: P3)

**Goal**: Full Flappy Bird mechanics with scoring, high scores, death screens, and configurable modes.

**Independent Test**: Run `uvx flappy-claude` directly, play game, verify collision/scoring/high score persistence.

### Tests for User Story 3

- [x] T032 [P] [US3] Create test_scores.py with test for load_high_score() when file missing in tests/test_scores.py
- [x] T033 [P] [US3] Add test for load_high_score() when file exists with valid score in tests/test_scores.py
- [x] T034 [P] [US3] Add test for save_high_score() creates directory and writes score in tests/test_scores.py
- [x] T035 [P] [US3] Create test_entities.py with tests for Bird.flap() and Bird.update() methods in tests/test_entities.py

### Implementation for User Story 3

- [x] T036 [P] [US3] Implement load_high_score(path) function in flappy_claude/scores.py
- [x] T037 [P] [US3] Implement save_high_score(path, score) function in flappy_claude/scores.py
- [x] T038 [US3] Add Bird.flap() method that sets upward velocity in flappy_claude/entities.py
- [x] T039 [US3] Add Bird.update(config) method that applies gravity in flappy_claude/entities.py
- [x] T040 [US3] Add Pipe.update(config) method that moves pipe left in flappy_claude/entities.py
- [x] T041 [US3] Implement pipe spawning logic (spacing, random gap position) in flappy_claude/game.py
- [x] T042 [US3] Implement render_death_screen(state) for auto-restart mode in flappy_claude/game.py
- [x] T043 [US3] Implement render_game_over_screen(state) for single-life mode in flappy_claude/game.py
- [x] T044 [US3] Add DEAD state handling: show death screen, auto-restart or wait for input in flappy_claude/game.py
- [x] T045 [US3] Integrate high score loading on game start in flappy_claude/game.py
- [x] T046 [US3] Integrate high score saving when new high score achieved in flappy_claude/game.py
- [x] T047 [US3] Add score display and high score display to game UI in flappy_claude/game.py

**Checkpoint**: User Story 3 complete - full game with all mechanics working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, cleanup, and validation

- [x] T048 Add graceful Ctrl+C handling with terminal cleanup in flappy_claude/game.py
- [x] T049 Add terminal capability check with friendly error message in flappy_claude/__main__.py
- [x] T050 [P] Add hook installation instructions to README or CLAUDE.md
- [x] T051 Run full test suite: `uv run pytest` and verify all tests pass
- [x] T052 Test zero-install experience: `uvx .` from project root
- [x] T053 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - core playable game
- **User Story 2 (Phase 4)**: Depends on US1 - adds IPC integration
- **User Story 3 (Phase 5)**: Can run parallel with US2 after US1 - adds full mechanics
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Requires Foundational only - builds core game
- **User Story 2 (P2)**: Requires US1 complete - game must exist to show prompts
- **User Story 3 (P3)**: Requires US1 complete - enhances existing game

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per Constitution)
- Physics module before game loop
- Entity methods before game integration
- Core feature before polish

### Parallel Opportunities

- T002, T003, T004 (Setup files) can run in parallel
- T006, T007, T008 (Entity definitions) can run in parallel
- T010-T013 (US1 tests) can run in parallel
- T014-T016 (Physics functions) can run in parallel
- T024, T025 (IPC functions) can run in parallel
- T032-T035 (US3 tests) can run in parallel
- T036, T037 (Score functions) can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all physics tests together:
Task: "Create test_physics.py with test for apply_gravity()"
Task: "Add test for check_collision() with boundaries"
Task: "Add test for check_collision() with pipe"
Task: "Add test for check_pipe_passed() scoring"

# Then launch all physics implementations together:
Task: "Implement apply_gravity(bird, config)"
Task: "Implement check_collision(bird, pipes, screen_height)"
Task: "Implement check_pipe_passed(bird, pipe)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `uv run python -m flappy_claude`, verify game plays
5. Test hook: install pretooluse.sh, trigger tool use, verify prompt and launch

### Incremental Delivery

1. Setup + Foundational → Package structure ready
2. User Story 1 → Playable game with hook launch (MVP!)
3. User Story 2 → Return-to-Claude integration
4. User Story 3 → Full game polish with high scores
5. Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Tests required for physics.py, scores.py, entities.py per Constitution Principle III
- Commit after each task or logical group
- Constitution: <500 lines per file, prefer simplicity
