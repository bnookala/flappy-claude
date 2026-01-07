"""Game configuration constants."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Game configuration with all tunable parameters."""

    # Physics
    gravity: float = 0.5
    flap_strength: float = -2.0
    terminal_velocity: float = 8.0

    # Pipes
    pipe_speed: int = 1
    pipe_gap: int = 7
    pipe_spacing: int = 25
    pipe_width: int = 4

    # Display
    fps: int = 30
    screen_width: int = 60
    screen_height: int = 20

    # Timing
    death_display_time: float = 1.0

    # Files
    high_score_path: str = "~/.flappy-claude/highscore"
    signal_file_path: str = "/tmp/flappy-claude-signal"


# Default configuration instance
DEFAULT_CONFIG = Config()
