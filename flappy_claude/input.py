"""Non-blocking keyboard input handling."""

import sys
import select
import termios
import tty
from contextlib import contextmanager
from typing import Generator


@contextmanager
def raw_terminal() -> Generator[None, None, None]:
    """Context manager for raw terminal mode.

    Saves and restores terminal settings.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_key_nonblocking() -> str | None:
    """Get a key press without blocking.

    Returns:
        The character pressed, or None if no key was pressed.
    """
    # Check if stdin has data available
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def get_key_blocking_with_timeout(timeout: float = 0.5) -> str | None:
    """Get a key press with timeout.

    Args:
        timeout: Maximum time to wait for input in seconds.

    Returns:
        The character pressed, or None if timeout.
    """
    if select.select([sys.stdin], [], [], timeout)[0]:
        return sys.stdin.read(1)
    return None
