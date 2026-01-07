"""Game configuration constants."""

import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Game configuration with all tunable parameters."""

    # Physics (forgiving settings)
    gravity: float = 0.3
    flap_strength: float = -1.5
    terminal_velocity: float = 6.0

    # Pipes (more forgiving)
    pipe_speed: int = 1
    pipe_gap: int = 12
    pipe_spacing: int = 35
    pipe_width: int = 3

    # Display
    fps: int = 30
    screen_width: int = 60
    screen_height: int = 20

    # Timing
    death_display_time: float = 1.0

    # Files
    high_score_path: str = "~/.flappy-claude/highscore"
    signal_file_path: str = "/tmp/flappy-claude-signal"


def get_terminal_config() -> Config:
    """Create a Config based on current terminal size."""
    size = shutil.get_terminal_size((80, 24))
    # Leave room for panel borders and padding
    width = max(40, size.columns - 4)
    height = max(15, size.lines - 8)

    # Gap should be about 40% of screen height - very forgiving
    pipe_gap = max(8, int(height * 0.4))

    return Config(
        screen_width=width,
        screen_height=height,
        pipe_gap=pipe_gap,
    )


# Default configuration instance
DEFAULT_CONFIG = Config()
