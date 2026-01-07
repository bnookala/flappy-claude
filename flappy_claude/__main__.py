"""Entry point for running flappy_claude as a module."""

import argparse
import sys
from pathlib import Path

from flappy_claude import __version__
from flappy_claude.config import get_terminal_config
from flappy_claude.entities import GameMode, GameState
from flappy_claude.game import run_game_loop
from flappy_claude.scores import load_high_score


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="flappy-claude",
        description="A terminal Flappy Bird game for Claude Code wait times",
    )

    parser.add_argument(
        "-s",
        "--single-life",
        action="store_true",
        help="Exit after first death instead of auto-restart",
    )

    parser.add_argument(
        "--signal-file",
        type=Path,
        default=Path("/tmp/flappy-claude-signal"),
        help="Path to IPC signal file for Claude integration",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args()


def check_terminal() -> bool:
    """Check if the terminal supports the game.

    Returns:
        True if terminal is suitable, False otherwise
    """
    if not sys.stdin.isatty():
        print("Error: flappy-claude requires an interactive terminal.")
        print("Please run from a terminal with keyboard input support.")
        return False

    if not sys.stdout.isatty():
        print("Error: flappy-claude requires a terminal display.")
        print("Please run from a terminal that supports curses.")
        return False

    return True


def main() -> None:
    """Main entry point for the game."""
    args = parse_args()

    # Check terminal capabilities
    if not check_terminal():
        sys.exit(1)

    # Determine game mode
    mode = GameMode.SINGLE_LIFE if args.single_life else GameMode.AUTO_RESTART

    # Create initial game state with terminal-sized config
    config = get_terminal_config()
    high_score_path = Path(config.high_score_path).expanduser()
    high_score = load_high_score(high_score_path)
    state = GameState.new_game(config, mode=mode, high_score=high_score)

    # Run the game
    try:
        run_game_loop(state, config, signal_file=args.signal_file)
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C

    sys.exit(0)


if __name__ == "__main__":
    main()
