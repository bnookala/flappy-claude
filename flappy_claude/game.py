"""Core game loop and rendering with Rich."""

import random
import sys
import time
from pathlib import Path

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from flappy_claude.config import Config, DEFAULT_CONFIG
from flappy_claude.entities import Bird, GameMode, GameState, GameStatus, Pipe
from flappy_claude.input import get_key_nonblocking
from flappy_claude.ipc import check_signal_file, delete_signal_file
from flappy_claude.physics import apply_gravity, check_collision, check_pipe_passed
from flappy_claude.scores import save_high_score


def render_game(state: GameState, config: Config) -> Panel:
    """Render the game state as a Rich Panel.

    Args:
        state: Current game state
        config: Game configuration

    Returns:
        Rich Panel containing the game display
    """
    # Create game grid
    lines = []

    # Header with score
    header = Text()
    header.append(f" Score: {state.score}", style="bold green")
    header.append("  |  ", style="dim")
    header.append(f"High: {state.high_score}", style="bold yellow")
    header.append("  |  ", style="dim")
    header.append("🎮", style="bold")
    lines.append(header)
    lines.append(Text("─" * config.screen_width, style="dim"))

    # Game area
    for row in range(config.screen_height):
        line = Text()
        for col in range(config.screen_width):
            char = _get_char_at(state, config, col, row)
            line.append(char)
        lines.append(line)

    # Footer with controls
    lines.append(Text("─" * config.screen_width, style="dim"))
    footer = Text(" SPACE to flap | Q to quit", style="dim italic")
    lines.append(footer)

    # Combine all lines
    content = Group(*lines)

    return Panel(
        content,
        title="[bold blue]Flappy Claude[/bold blue]",
        border_style="blue",
    )


def render_claude_ready_prompt(state: GameState, config: Config) -> Panel:
    """Render the Claude ready prompt overlay.

    Args:
        state: Current game state
        config: Game configuration

    Returns:
        Rich Panel with the prompt overlay
    """
    # Create a simpler overlay
    lines = []
    lines.append(Text())
    lines.append(Text())
    lines.append(Text("  ╔════════════════════════════════╗  ", style="bold cyan"))
    lines.append(Text("  ║                                ║  ", style="bold cyan"))
    lines.append(Text("  ║    ✨ Claude is ready! ✨      ║  ", style="bold cyan"))
    lines.append(Text("  ║                                ║  ", style="bold cyan"))
    lines.append(Text("  ║   Return to session? (y/n)     ║  ", style="bold cyan"))
    lines.append(Text("  ║                                ║  ", style="bold cyan"))
    lines.append(Text("  ╚════════════════════════════════╝  ", style="bold cyan"))
    lines.append(Text())
    lines.append(Text(f"          Current Score: {state.score}", style="bold green"))
    lines.append(Text())

    content = Group(*lines)

    return Panel(
        Align.center(content),
        title="[bold blue]Flappy Claude[/bold blue]",
        border_style="cyan",
    )


def render_death_screen(state: GameState, config: Config) -> Panel:
    """Render the death screen for auto-restart mode.

    Args:
        state: Current game state
        config: Game configuration

    Returns:
        Rich Panel with death screen
    """
    lines = []
    lines.append(Text())
    lines.append(Text())
    lines.append(Text("         💀 Score: " + str(state.score), style="bold red"))
    lines.append(Text())
    lines.append(Text("         High Score: " + str(state.high_score), style="bold yellow"))
    lines.append(Text())
    lines.append(Text("         Restarting...", style="dim italic"))
    lines.append(Text())

    content = Group(*lines)

    return Panel(
        Align.center(content),
        title="[bold blue]Flappy Claude[/bold blue]",
        border_style="red",
    )


def render_game_over_screen(state: GameState, config: Config) -> Panel:
    """Render the game over screen for single-life mode.

    Args:
        state: Current game state
        config: Game configuration

    Returns:
        Rich Panel with game over screen
    """
    lines = []
    lines.append(Text())
    lines.append(Text())
    lines.append(Text("         💀 Game Over!", style="bold red"))
    lines.append(Text())
    lines.append(Text("         Score: " + str(state.score), style="bold green"))
    lines.append(Text())
    lines.append(Text("         High Score: " + str(state.high_score), style="bold yellow"))
    lines.append(Text())
    lines.append(Text("         Press any key to exit", style="dim italic"))
    lines.append(Text())

    content = Group(*lines)

    return Panel(
        Align.center(content),
        title="[bold blue]Flappy Claude[/bold blue]",
        border_style="red",
    )


def _get_char_at(state: GameState, config: Config, col: int, row: int) -> str:
    """Get the character to display at a specific position.

    Args:
        state: Current game state
        config: Game configuration
        col: Column position
        row: Row position

    Returns:
        Character to display
    """
    # Check if bird is at this position
    bird_row = int(state.bird.y)
    if col == state.bird.x and row == bird_row:
        return "🐦"

    # Check if any pipe is at this position
    for pipe in state.pipes:
        if _is_pipe_at(pipe, config, col, row):
            return "█"

    return " "


def _is_pipe_at(pipe: Pipe, config: Config, col: int, row: int) -> bool:
    """Check if a pipe occupies a specific position.

    Args:
        pipe: The pipe to check
        config: Game configuration
        col: Column position
        row: Row position

    Returns:
        True if pipe is at this position
    """
    # Check horizontal bounds
    if col < pipe.x or col >= pipe.x + config.pipe_width:
        return False

    # Check if in gap
    gap_top = int(pipe.gap_y - pipe.gap_size / 2)
    gap_bottom = int(pipe.gap_y + pipe.gap_size / 2)

    if gap_top <= row <= gap_bottom:
        return False

    return True


def spawn_pipe(state: GameState, config: Config) -> None:
    """Spawn a new pipe at the right edge of the screen.

    Args:
        state: Current game state (modified in place)
        config: Game configuration
    """
    # Random gap position, avoiding edges
    margin = config.pipe_gap // 2 + 2
    gap_y = random.randint(margin, config.screen_height - margin)

    pipe = Pipe(
        x=config.screen_width,
        gap_y=gap_y,
        gap_size=config.pipe_gap,
    )
    state.pipes.append(pipe)


def update_game(state: GameState, config: Config) -> None:
    """Update game state for one frame.

    Args:
        state: Current game state (modified in place)
        config: Game configuration
    """
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

    # Spawn new pipes
    if not state.pipes or state.pipes[-1].x < config.screen_width - config.pipe_spacing:
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


def handle_input(state: GameState, config: Config, key: str | None) -> None:
    """Handle keyboard input.

    Args:
        state: Current game state (modified in place)
        config: Game configuration
        key: Key pressed, or None
    """
    if key is None:
        return

    key_lower = key.lower()

    if key_lower == "q" or key == "\x03":  # q or Ctrl+C
        state.status = GameStatus.EXITING
    elif key == " " and state.status == GameStatus.PLAYING:
        state.bird.flap(config)
    elif key_lower in ("y", "n") and state.status == GameStatus.PROMPTED:
        if key_lower == "y":
            state.status = GameStatus.EXITING
        else:
            state.claude_ready = False  # Dismiss prompt
            state.status = GameStatus.PLAYING


def get_render_for_state(state: GameState, config: Config) -> Panel:
    """Get the appropriate render for the current game state.

    Args:
        state: Current game state
        config: Game configuration

    Returns:
        Rich Panel for the current state
    """
    if state.status == GameStatus.PROMPTED:
        return render_claude_ready_prompt(state, config)
    elif state.status == GameStatus.DEAD:
        if state.mode == GameMode.SINGLE_LIFE:
            return render_game_over_screen(state, config)
        else:
            return render_death_screen(state, config)
    else:
        return render_game(state, config)


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
    import termios
    import tty

    console = Console()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)

        with Live(
            get_render_for_state(state, config),
            console=console,
            refresh_per_second=config.fps,
            transient=True,
        ) as live:
            frame_time = 1.0 / config.fps

            while state.status != GameStatus.EXITING:
                start = time.time()

                # Handle input
                key = get_key_nonblocking()
                handle_input(state, config, key)

                # Check signal file for Claude ready (only when playing)
                if signal_file and state.status == GameStatus.PLAYING:
                    if not state.claude_ready and check_signal_file(signal_file):
                        state.claude_ready = True
                        state.status = GameStatus.PROMPTED

                # Update game
                update_game(state, config)

                # Handle death
                if state.status == GameStatus.DEAD:
                    live.update(get_render_for_state(state, config))
                    if state.mode == GameMode.AUTO_RESTART:
                        time.sleep(config.death_display_time)
                        state.reset(config)
                    else:
                        # Single life mode - wait for any key then exit
                        while True:
                            k = get_key_nonblocking()
                            if k:
                                break
                            time.sleep(0.05)
                        state.status = GameStatus.EXITING

                # Update display
                live.update(get_render_for_state(state, config))

                # Frame timing
                elapsed = time.time() - start
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # Clean up signal file
        if signal_file:
            delete_signal_file(signal_file)
