"""Core game loop and rendering with curses."""

import curses
import random
import time
from pathlib import Path

from flappy_claude.config import Config
from flappy_claude.entities import Bird, GameMode, GameState, GameStatus, Pipe
from flappy_claude.ipc import check_signal_file, delete_signal_file
from flappy_claude.physics import apply_gravity, check_collision, check_pipe_passed
from flappy_claude.scores import save_high_score


def render_game(stdscr, state: GameState, config: Config) -> None:
    """Render the game state using curses.

    Args:
        stdscr: curses window
        state: Current game state
        config: Game configuration
    """
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    # Draw border
    try:
        stdscr.attron(curses.color_pair(1))
        stdscr.border()
        stdscr.attroff(curses.color_pair(1))
    except curses.error:
        pass

    # Draw header
    if state.claude_ready and state.status == GameStatus.PLAYING:
        # Claude finished but user chose to keep playing - show blinking indicator
        header = f" Score: {state.score}  |  High: {state.high_score}  |  CLAUDE WAITING "
        header_color = curses.color_pair(3) | curses.A_BOLD | curses.A_BLINK
    else:
        header = f" Score: {state.score}  |  High: {state.high_score}  |  Flappy Claude "
        header_color = curses.color_pair(2) | curses.A_BOLD
    try:
        stdscr.addstr(0, max(0, (max_x - len(header)) // 2), header, header_color)
    except curses.error:
        pass

    # Draw game area
    bird_row = int(state.bird.y)
    for row in range(config.screen_height):
        for col in range(config.screen_width):
            screen_row = row + 2  # Offset for header
            screen_col = col + 2  # Offset for border

            if screen_row >= max_y - 1 or screen_col >= max_x - 2:
                continue

            # Skip the column after the crab (emoji is 2 chars wide)
            if col == state.bird.x + 1 and row == bird_row:
                continue

            char = _get_char_at(state, config, col, row)
            try:
                if char == "🦀":  # Crab
                    stdscr.addstr(screen_row, screen_col, char, curses.color_pair(3) | curses.A_BOLD)
                elif char == "█":  # Pipe
                    stdscr.addstr(screen_row, screen_col, char, curses.color_pair(4))
                else:
                    stdscr.addstr(screen_row, screen_col, char)
            except curses.error:
                pass

    # Draw footer
    if state.claude_ready and state.status == GameStatus.PLAYING:
        footer = " SPACE=flap  Y=return to Claude  Q=quit "
    else:
        footer = " SPACE=flap  Q=quit "
    try:
        stdscr.addstr(max_y - 1, max(0, (max_x - len(footer)) // 2), footer, curses.color_pair(5))
    except curses.error:
        pass

    stdscr.refresh()


def render_overlay(stdscr, title: str, lines: list[str], config: Config) -> None:
    """Render a centered overlay box.

    Args:
        stdscr: curses window
        title: Overlay title
        lines: Lines of text to display
        config: Game configuration
    """
    max_y, max_x = stdscr.getmaxyx()

    # Calculate box dimensions
    box_width = max(len(line) for line in lines) + 6
    box_height = len(lines) + 4
    start_y = (max_y - box_height) // 2
    start_x = (max_x - box_width) // 2

    # Draw box
    try:
        for i in range(box_height):
            y = start_y + i
            if y < 0 or y >= max_y:
                continue

            if i == 0:
                line = "╔" + "═" * (box_width - 2) + "╗"
            elif i == box_height - 1:
                line = "╚" + "═" * (box_width - 2) + "╝"
            else:
                line = "║" + " " * (box_width - 2) + "║"

            stdscr.addstr(y, start_x, line, curses.color_pair(6) | curses.A_BOLD)

        # Draw title
        title_x = start_x + (box_width - len(title)) // 2
        stdscr.addstr(start_y, title_x, title, curses.color_pair(6) | curses.A_BOLD)

        # Draw content lines
        for i, line in enumerate(lines):
            y = start_y + 2 + i
            x = start_x + (box_width - len(line)) // 2
            if y < max_y and x < max_x:
                stdscr.addstr(y, x, line, curses.color_pair(2))

    except curses.error:
        pass

    stdscr.refresh()


def render_claude_ready_prompt(stdscr, state: GameState, config: Config, countdown: int) -> None:
    """Render the Claude ready prompt overlay with countdown."""
    render_game(stdscr, state, config)

    if state.was_playing:
        # User was actively playing
        lines = [
            "Claude has finished!",
            "",
            f"Your Score: {state.score}",
            "",
            "[Y] Return to Claude",
            "[N] Keep playing",
            "",
            f"Auto-closing in {countdown}s...",
        ]
    else:
        # User was on waiting screen
        lines = [
            "Claude has finished!",
            "",
            "[Y] Return to Claude",
            "[N] Start playing anyway",
            "",
            f"Auto-closing in {countdown}s...",
        ]

    render_overlay(stdscr, " Claude Ready! ", lines, config)


def render_death_screen(stdscr, state: GameState, config: Config) -> None:
    """Render the death screen for auto-restart mode."""
    render_game(stdscr, state, config)
    render_overlay(
        stdscr,
        " Game Over ",
        [
            f"Score: {state.score}",
            f"High Score: {state.high_score}",
            "",
            "Restarting...",
        ],
        config,
    )


def render_game_over_screen(stdscr, state: GameState, config: Config) -> None:
    """Render the game over screen for single-life mode."""
    render_game(stdscr, state, config)
    render_overlay(
        stdscr,
        " Game Over ",
        [
            f"Final Score: {state.score}",
            f"High Score: {state.high_score}",
            "",
            "Press any key to exit",
        ],
        config,
    )


def render_waiting_screen(stdscr, state: GameState, config: Config) -> None:
    """Render the waiting screen before game starts."""
    render_game(stdscr, state, config)
    render_overlay(
        stdscr,
        " Flappy Claude ",
        [
            "Play while Claude works!",
            "",
            f"High Score: {state.high_score}",
            "",
            "Press SPACE to start",
        ],
        config,
    )


def _get_char_at(state: GameState, config: Config, col: int, row: int) -> str:
    """Get the character to display at a specific position."""
    # Check if bird is at this position
    bird_row = int(state.bird.y)
    if col == state.bird.x and row == bird_row:
        return "🦀"

    # Check if any pipe is at this position
    for pipe in state.pipes:
        if _is_pipe_at(pipe, config, col, row):
            return "█"

    return " "


def _is_pipe_at(pipe: Pipe, config: Config, col: int, row: int) -> bool:
    """Check if a pipe occupies a specific position."""
    # Check horizontal bounds
    if col < pipe.x or col >= pipe.x + config.pipe_width:
        return False

    # Check if in gap
    gap_top = int(pipe.gap_y - pipe.gap_size / 2)
    gap_bottom = int(pipe.gap_y + pipe.gap_size / 2)

    if gap_top <= row <= gap_bottom:
        return False

    return True


def get_difficulty_params(score: int, config: Config) -> tuple[int, int]:
    """Calculate difficulty parameters based on score.

    Returns:
        tuple of (gap_size, pipe_spacing)
    """
    # Gap shrinks from base gap to minimum of 6, decreasing every 5 points
    base_gap = config.pipe_gap
    min_gap = 6
    gap_reduction = min(score // 5, (base_gap - min_gap))
    current_gap = base_gap - gap_reduction

    # Spacing shrinks from 35 to minimum of 20, decreasing every 3 points
    base_spacing = config.pipe_spacing
    min_spacing = 20
    spacing_reduction = min(score // 3, (base_spacing - min_spacing))
    current_spacing = base_spacing - spacing_reduction

    return current_gap, current_spacing


def spawn_pipe(state: GameState, config: Config) -> None:
    """Spawn a new pipe at the right edge of the screen."""
    # Get difficulty-adjusted gap size
    current_gap, _ = get_difficulty_params(state.score, config)

    # Ensure gap is fully visible with padding from edges
    half_gap = current_gap // 2
    min_gap_y = half_gap + 2
    max_gap_y = config.screen_height - half_gap - 2

    # Safety check - ensure valid range
    if max_gap_y <= min_gap_y:
        gap_y = config.screen_height // 2
    else:
        gap_y = random.randint(min_gap_y, max_gap_y)

    pipe = Pipe(
        x=config.screen_width,
        gap_y=gap_y,
        gap_size=current_gap,
    )
    state.pipes.append(pipe)


def update_game(state: GameState, config: Config) -> None:
    """Update game state for one frame."""
    if state.status != GameStatus.PLAYING:
        return

    # Update bird
    updated_bird = apply_gravity(state.bird, config)
    state.bird.y = updated_bird.y
    state.bird.velocity = updated_bird.velocity

    # Update pipes
    for pipe in state.pipes:
        pipe.update(config)

    # Remove off-screen pipes
    state.pipes = [p for p in state.pipes if p.x > -config.pipe_width]

    # Spawn new pipes (spacing decreases with difficulty)
    _, current_spacing = get_difficulty_params(state.score, config)
    if not state.pipes or state.pipes[-1].x < config.screen_width - current_spacing:
        spawn_pipe(state, config)

    # Check scoring
    for pipe in state.pipes:
        if not pipe.passed and check_pipe_passed(state.bird, pipe):
            pipe.mark_passed()
            state.score += 1
            if state.score > state.high_score:
                state.high_score = state.score
                # Save new high score immediately
                high_score_path = Path(config.high_score_path).expanduser()
                save_high_score(high_score_path, state.high_score)

    # Check collision
    if check_collision(state.bird, state.pipes, config.screen_height):
        state.status = GameStatus.DEAD


def handle_input(state: GameState, config: Config, key: int) -> None:
    """Handle keyboard input.

    Args:
        state: Current game state (modified in place)
        config: Game configuration
        key: Key code from curses, or -1 for no input
    """
    if key == -1:
        return

    if key in (ord('q'), ord('Q'), 27):  # q, Q, or ESC
        state.status = GameStatus.EXITING
    elif key == ord(' ') and state.status == GameStatus.WAITING:
        state.status = GameStatus.PLAYING
    elif key == ord(' ') and state.status == GameStatus.PLAYING:
        state.bird.flap(config)
    elif key in (ord('y'), ord('Y')) and state.status == GameStatus.PROMPTED:
        state.status = GameStatus.EXITING
    elif key in (ord('n'), ord('N')) and state.status == GameStatus.PROMPTED:
        # Keep claude_ready=True so we show "CLAUDE WAITING" header
        state.status = GameStatus.PLAYING
    elif key in (ord('y'), ord('Y')) and state.status == GameStatus.PLAYING and state.claude_ready:
        # Allow returning to Claude while playing if Claude is waiting
        state.status = GameStatus.EXITING


def init_colors() -> None:
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()

    # Color pairs: (foreground, background)
    curses.init_pair(1, curses.COLOR_BLUE, -1)      # Border
    curses.init_pair(2, curses.COLOR_GREEN, -1)     # Score/text
    curses.init_pair(3, curses.COLOR_YELLOW, -1)    # Bird
    curses.init_pair(4, curses.COLOR_GREEN, -1)     # Pipes
    curses.init_pair(5, curses.COLOR_WHITE, -1)     # Footer
    curses.init_pair(6, curses.COLOR_CYAN, -1)      # Overlay


def game_main(stdscr, state: GameState, config: Config, signal_file: Path | None) -> None:
    """Main game loop running inside curses wrapper.

    Args:
        stdscr: curses window
        state: Initial game state
        config: Game configuration
        signal_file: Optional path to signal file for Claude integration
    """
    # Setup curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(1000 // config.fps)  # Input timeout for frame rate
    init_colors()

    frame_time = 1.0 / config.fps

    try:
        while state.status != GameStatus.EXITING:
            start = time.time()

            # Handle input
            key = stdscr.getch()
            handle_input(state, config, key)

            # Check signal file for Claude ready (when waiting or playing)
            if signal_file and state.status in (GameStatus.WAITING, GameStatus.PLAYING):
                if not state.claude_ready and check_signal_file(signal_file):
                    state.claude_ready = True
                    state.was_playing = (state.status == GameStatus.PLAYING)
                    state.prompted_at = time.time()
                    state.status = GameStatus.PROMPTED

            # Update game
            update_game(state, config)

            # Render based on state
            if state.status == GameStatus.WAITING:
                render_waiting_screen(stdscr, state, config)
            elif state.status == GameStatus.PROMPTED:
                # Calculate countdown (10 seconds)
                elapsed = time.time() - state.prompted_at
                countdown = max(0, 10 - int(elapsed))
                if countdown <= 0:
                    state.status = GameStatus.EXITING
                else:
                    render_claude_ready_prompt(stdscr, state, config, countdown)
            elif state.status == GameStatus.DEAD:
                if state.mode == GameMode.SINGLE_LIFE:
                    render_game_over_screen(stdscr, state, config)
                    # Wait for any key
                    stdscr.nodelay(False)
                    stdscr.getch()
                    state.status = GameStatus.EXITING
                else:
                    render_death_screen(stdscr, state, config)
                    time.sleep(config.death_display_time)
                    state.reset(config)
            else:
                render_game(stdscr, state, config)

            # Frame timing
            elapsed = time.time() - start
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    finally:
        # Clean up signal file
        if signal_file:
            delete_signal_file(signal_file)


def run_game_loop(
    state: GameState,
    config: Config,
    signal_file: Path | None = None,
) -> None:
    """Run the main game loop.

    Args:
        state: Initial game state
        config: Game configuration
        signal_file: Optional path to signal file for Claude integration
    """
    curses.wrapper(lambda stdscr: game_main(stdscr, state, config, signal_file))
