"""Game entities: Bird, Pipe, GameState."""

from dataclasses import dataclass, field
from enum import Enum, auto

from flappy_claude.config import Config


class GameStatus(Enum):
    """Current game phase."""

    PLAYING = auto()
    DEAD = auto()
    PROMPTED = auto()
    EXITING = auto()


class GameMode(Enum):
    """Game over behavior mode."""

    AUTO_RESTART = auto()
    SINGLE_LIFE = auto()


@dataclass
class Bird:
    """The player-controlled character."""

    y: float
    velocity: float = 0.0
    x: int = 15  # Fixed horizontal position

    def flap(self, config: Config) -> None:
        """Apply upward velocity for a flap."""
        self.velocity = config.flap_strength

    def update(self, config: Config) -> None:
        """Apply gravity and update position."""
        self.velocity += config.gravity
        self.velocity = min(self.velocity, config.terminal_velocity)
        self.y += self.velocity


@dataclass
class Pipe:
    """An obstacle the bird must navigate through."""

    x: int
    gap_y: int
    gap_size: int
    passed: bool = False

    def update(self, config: Config) -> None:
        """Move pipe leftward."""
        self.x -= config.pipe_speed

    def mark_passed(self) -> None:
        """Mark this pipe as passed for scoring."""
        self.passed = True


@dataclass
class GameState:
    """Overall game state container."""

    bird: Bird
    pipes: list[Pipe] = field(default_factory=list)
    score: int = 0
    high_score: int = 0
    status: GameStatus = GameStatus.PLAYING
    mode: GameMode = GameMode.AUTO_RESTART
    claude_ready: bool = False

    @classmethod
    def new_game(
        cls,
        config: Config,
        mode: GameMode = GameMode.AUTO_RESTART,
        high_score: int = 0,
    ) -> "GameState":
        """Create a new game state with bird at starting position."""
        bird = Bird(y=config.screen_height // 2, x=config.screen_width // 4)
        return cls(bird=bird, mode=mode, high_score=high_score)

    def reset(self, config: Config) -> None:
        """Reset game state for a new round (keeps high score and mode)."""
        self.bird = Bird(y=config.screen_height // 2, x=config.screen_width // 4)
        self.pipes = []
        self.score = 0
        self.status = GameStatus.PLAYING
        self.claude_ready = False
