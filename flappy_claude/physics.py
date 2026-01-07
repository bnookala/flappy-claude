"""Physics functions: gravity, collision detection, scoring."""

from flappy_claude.config import Config
from flappy_claude.entities import Bird, Pipe


def apply_gravity(bird: Bird, config: Config) -> Bird:
    """Apply gravity to bird and update position.

    Returns a new Bird with updated velocity and position.
    """
    new_velocity = bird.velocity + config.gravity
    new_velocity = min(new_velocity, config.terminal_velocity)
    new_y = bird.y + new_velocity

    return Bird(y=new_y, velocity=new_velocity, x=bird.x)


def check_collision(bird: Bird, pipes: list[Pipe], screen_height: int) -> bool:
    """Check if bird collides with boundaries or pipes.

    Args:
        bird: The bird to check
        pipes: List of pipes to check against
        screen_height: Height of the game screen

    Returns:
        True if collision detected, False otherwise
    """
    # Check boundary collision
    if bird.y < 0 or bird.y >= screen_height:
        return True

    # Check pipe collision
    for pipe in pipes:
        if _bird_hits_pipe(bird, pipe):
            return True

    return False


def _bird_hits_pipe(bird: Bird, pipe: Pipe) -> bool:
    """Check if bird collides with a specific pipe.

    A pipe has a gap in the middle. The bird collides if:
    1. Bird's x position overlaps with pipe's x position (within pipe width)
    2. Bird is NOT within the gap (above gap top or below gap bottom)
    """
    pipe_width = 4  # Default pipe width

    # Check horizontal overlap
    if not (bird.x >= pipe.x and bird.x < pipe.x + pipe_width):
        return False

    # Calculate gap boundaries
    gap_top = pipe.gap_y - pipe.gap_size / 2
    gap_bottom = pipe.gap_y + pipe.gap_size / 2

    # Bird collides if outside the gap
    if bird.y < gap_top or bird.y > gap_bottom:
        return True

    return False


def check_pipe_passed(bird: Bird, pipe: Pipe) -> bool:
    """Check if bird has passed a pipe for scoring.

    A pipe is passed when:
    1. Bird's x position is ahead of the pipe's x position
    2. OR the pipe was already marked as passed

    Args:
        bird: The bird
        pipe: The pipe to check

    Returns:
        True if pipe is passed, False otherwise
    """
    if pipe.passed:
        return True

    return bird.x > pipe.x
