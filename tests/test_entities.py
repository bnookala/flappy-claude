"""Tests for game entity methods."""

import pytest

from flappy_claude.config import Config, DEFAULT_CONFIG
from flappy_claude.entities import Bird, Pipe, GameState, GameStatus, GameMode


class TestBirdFlap:
    """Tests for Bird.flap() method."""

    def test_flap_sets_upward_velocity(self) -> None:
        """Bird.flap() sets velocity to flap_strength."""
        bird = Bird(y=10.0, velocity=2.0, x=5)
        config = DEFAULT_CONFIG

        bird.flap(config)

        assert bird.velocity == config.flap_strength

    def test_flap_overrides_downward_velocity(self) -> None:
        """Bird.flap() works even when falling fast."""
        bird = Bird(y=10.0, velocity=5.0, x=5)  # Falling fast
        config = DEFAULT_CONFIG

        bird.flap(config)

        assert bird.velocity == config.flap_strength
        assert bird.velocity < 0  # Moving upward

    def test_flap_does_not_change_position(self) -> None:
        """Bird.flap() doesn't immediately change y position."""
        bird = Bird(y=10.0, velocity=2.0, x=5)
        original_y = bird.y

        bird.flap(DEFAULT_CONFIG)

        assert bird.y == original_y


class TestBirdUpdate:
    """Tests for Bird.update() method."""

    def test_update_applies_gravity(self) -> None:
        """Bird.update() increases velocity by gravity."""
        bird = Bird(y=10.0, velocity=0.0, x=5)
        config = DEFAULT_CONFIG

        bird.update(config)

        assert bird.velocity == config.gravity

    def test_update_moves_bird_by_velocity(self) -> None:
        """Bird.update() changes y position by velocity."""
        bird = Bird(y=10.0, velocity=2.0, x=5)
        config = DEFAULT_CONFIG

        bird.update(config)

        # y should change by old velocity (2.0) after gravity applied
        # velocity becomes 2.0 + 0.5 = 2.5, y becomes 10 + 2.5 = 12.5
        assert bird.y == 10.0 + 2.0 + config.gravity

    def test_update_respects_terminal_velocity(self) -> None:
        """Bird.update() caps velocity at terminal_velocity."""
        bird = Bird(y=10.0, velocity=100.0, x=5)  # Way over terminal
        config = DEFAULT_CONFIG

        bird.update(config)

        assert bird.velocity == config.terminal_velocity

    def test_update_with_negative_velocity_moves_up(self) -> None:
        """Bird.update() moves bird up when velocity is negative."""
        bird = Bird(y=10.0, velocity=-2.0, x=5)
        config = DEFAULT_CONFIG

        bird.update(config)

        # Gravity slows the upward movement: -2.0 + 0.5 = -1.5
        # y becomes 10.0 + (-1.5) = 8.5
        assert bird.y < 10.0


class TestPipeUpdate:
    """Tests for Pipe.update() method."""

    def test_update_moves_pipe_left(self) -> None:
        """Pipe.update() decreases x by pipe_speed."""
        pipe = Pipe(x=50, gap_y=10, gap_size=7)
        config = DEFAULT_CONFIG

        pipe.update(config)

        assert pipe.x == 50 - config.pipe_speed

    def test_update_does_not_change_gap(self) -> None:
        """Pipe.update() doesn't modify gap position."""
        pipe = Pipe(x=50, gap_y=10, gap_size=7)
        original_gap_y = pipe.gap_y
        original_gap_size = pipe.gap_size

        pipe.update(DEFAULT_CONFIG)

        assert pipe.gap_y == original_gap_y
        assert pipe.gap_size == original_gap_size


class TestPipeMarkPassed:
    """Tests for Pipe.mark_passed() method."""

    def test_mark_passed_sets_passed_true(self) -> None:
        """Pipe.mark_passed() sets passed to True."""
        pipe = Pipe(x=5, gap_y=10, gap_size=7, passed=False)

        pipe.mark_passed()

        assert pipe.passed is True

    def test_mark_passed_is_idempotent(self) -> None:
        """Pipe.mark_passed() can be called multiple times."""
        pipe = Pipe(x=5, gap_y=10, gap_size=7, passed=True)

        pipe.mark_passed()  # Should not raise

        assert pipe.passed is True


class TestGameStateReset:
    """Tests for GameState.reset() method."""

    def test_reset_clears_score(self) -> None:
        """GameState.reset() sets score to 0."""
        state = GameState.new_game(DEFAULT_CONFIG)
        state.score = 50

        state.reset(DEFAULT_CONFIG)

        assert state.score == 0

    def test_reset_preserves_high_score(self) -> None:
        """GameState.reset() keeps the high score."""
        state = GameState.new_game(DEFAULT_CONFIG)
        state.high_score = 100
        state.score = 50

        state.reset(DEFAULT_CONFIG)

        assert state.high_score == 100

    def test_reset_clears_pipes(self) -> None:
        """GameState.reset() removes all pipes."""
        state = GameState.new_game(DEFAULT_CONFIG)
        state.pipes.append(Pipe(x=30, gap_y=10, gap_size=7))

        state.reset(DEFAULT_CONFIG)

        assert len(state.pipes) == 0

    def test_reset_resets_bird_position(self) -> None:
        """GameState.reset() puts bird back at starting position."""
        config = DEFAULT_CONFIG
        state = GameState.new_game(config)
        state.bird.y = 0.0
        state.bird.velocity = 10.0

        state.reset(config)

        assert state.bird.y == config.screen_height / 2
        assert state.bird.velocity == 0.0

    def test_reset_sets_status_to_playing(self) -> None:
        """GameState.reset() sets status back to PLAYING."""
        state = GameState.new_game(DEFAULT_CONFIG)
        state.status = GameStatus.DEAD

        state.reset(DEFAULT_CONFIG)

        assert state.status == GameStatus.PLAYING

    def test_reset_preserves_mode(self) -> None:
        """GameState.reset() keeps the game mode."""
        state = GameState.new_game(DEFAULT_CONFIG, mode=GameMode.SINGLE_LIFE)

        state.reset(DEFAULT_CONFIG)

        assert state.mode == GameMode.SINGLE_LIFE
