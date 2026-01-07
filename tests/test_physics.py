"""Tests for physics module - collision, gravity, scoring."""

import pytest

from flappy_claude.config import Config
from flappy_claude.entities import Bird, Pipe


# Test fixtures
@pytest.fixture
def config() -> Config:
    """Default game configuration."""
    return Config()


@pytest.fixture
def bird(config: Config) -> Bird:
    """Bird at center of screen."""
    return Bird(y=config.screen_height // 2, x=config.screen_width // 4)


# T010: Test apply_gravity
class TestApplyGravity:
    """Tests for apply_gravity function."""

    def test_apply_gravity_increases_velocity(self, config: Config) -> None:
        """Gravity should increase bird's downward velocity."""
        from flappy_claude.physics import apply_gravity

        bird = Bird(y=10.0, velocity=0.0)
        updated_bird = apply_gravity(bird, config)

        assert updated_bird.velocity == config.gravity

    def test_apply_gravity_updates_position(self, config: Config) -> None:
        """Gravity should update bird's y position based on velocity."""
        from flappy_claude.physics import apply_gravity

        bird = Bird(y=10.0, velocity=1.0)
        updated_bird = apply_gravity(bird, config)

        # New velocity = 1.0 + 0.5 = 1.5, new y = 10.0 + 1.5 = 11.5
        assert updated_bird.y == 10.0 + 1.0 + config.gravity

    def test_apply_gravity_respects_terminal_velocity(self, config: Config) -> None:
        """Velocity should not exceed terminal velocity."""
        from flappy_claude.physics import apply_gravity

        bird = Bird(y=10.0, velocity=config.terminal_velocity)
        updated_bird = apply_gravity(bird, config)

        assert updated_bird.velocity <= config.terminal_velocity


# T011: Test collision with boundaries
class TestCollisionBoundaries:
    """Tests for check_collision with screen boundaries."""

    def test_collision_with_top(self, config: Config) -> None:
        """Bird hitting top of screen should be collision."""
        from flappy_claude.physics import check_collision

        bird = Bird(y=-1.0)
        assert check_collision(bird, [], config.screen_height) is True

    def test_collision_with_bottom(self, config: Config) -> None:
        """Bird hitting bottom of screen should be collision."""
        from flappy_claude.physics import check_collision

        bird = Bird(y=config.screen_height + 1)
        assert check_collision(bird, [], config.screen_height) is True

    def test_no_collision_in_bounds(self, config: Config) -> None:
        """Bird within screen bounds should not collide."""
        from flappy_claude.physics import check_collision

        bird = Bird(y=config.screen_height // 2)
        assert check_collision(bird, [], config.screen_height) is False


# T012: Test collision with pipes
class TestCollisionPipes:
    """Tests for check_collision with pipes."""

    def test_collision_with_top_pipe(self, config: Config) -> None:
        """Bird hitting top section of pipe should be collision."""
        from flappy_claude.physics import check_collision

        # Pipe with gap at y=10, gap_size=7, so top pipe ends at y=6.5
        pipe = Pipe(x=15, gap_y=10, gap_size=7)
        bird = Bird(y=3.0, x=15)  # Bird above the gap
        assert check_collision(bird, [pipe], config.screen_height) is True

    def test_collision_with_bottom_pipe(self, config: Config) -> None:
        """Bird hitting bottom section of pipe should be collision."""
        from flappy_claude.physics import check_collision

        # Pipe with gap at y=10, gap_size=7, so bottom pipe starts at y=13.5
        pipe = Pipe(x=15, gap_y=10, gap_size=7)
        bird = Bird(y=16.0, x=15)  # Bird below the gap
        assert check_collision(bird, [pipe], config.screen_height) is True

    def test_no_collision_through_gap(self, config: Config) -> None:
        """Bird passing through gap should not collide."""
        from flappy_claude.physics import check_collision

        pipe = Pipe(x=15, gap_y=10, gap_size=7)
        bird = Bird(y=10.0, x=15)  # Bird in center of gap
        assert check_collision(bird, [pipe], config.screen_height) is False

    def test_no_collision_before_pipe(self, config: Config) -> None:
        """Bird before pipe x position should not collide."""
        from flappy_claude.physics import check_collision

        pipe = Pipe(x=20, gap_y=10, gap_size=7)
        bird = Bird(y=5.0, x=10)  # Bird before the pipe
        assert check_collision(bird, [pipe], config.screen_height) is False


# T013: Test pipe passed scoring
class TestPipePassed:
    """Tests for check_pipe_passed scoring logic."""

    def test_pipe_passed_when_bird_ahead(self) -> None:
        """Pipe should be marked passed when bird is ahead of it."""
        from flappy_claude.physics import check_pipe_passed

        pipe = Pipe(x=10, gap_y=10, gap_size=7, passed=False)
        bird = Bird(y=10.0, x=15)  # Bird ahead of pipe

        assert check_pipe_passed(bird, pipe) is True

    def test_pipe_not_passed_when_bird_behind(self) -> None:
        """Pipe should not be passed when bird is behind it."""
        from flappy_claude.physics import check_pipe_passed

        pipe = Pipe(x=20, gap_y=10, gap_size=7, passed=False)
        bird = Bird(y=10.0, x=15)  # Bird behind pipe

        assert check_pipe_passed(bird, pipe) is False

    def test_already_passed_pipe(self) -> None:
        """Already passed pipe should still return True."""
        from flappy_claude.physics import check_pipe_passed

        pipe = Pipe(x=10, gap_y=10, gap_size=7, passed=True)
        bird = Bird(y=10.0, x=15)

        assert check_pipe_passed(bird, pipe) is True
