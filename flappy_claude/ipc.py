"""Inter-process communication via signal files."""

from enum import Enum, auto
from pathlib import Path


class SignalType(Enum):
    """Types of signals from Claude Code hooks."""

    NONE = auto()  # No signal or file doesn't exist
    READY = auto()  # Claude is done, user can return
    PAUSE = auto()  # Claude is asking a question, pause game


def read_signal(path: Path) -> SignalType:
    """Read the current signal from the signal file.

    Args:
        path: Path to the signal file

    Returns:
        SignalType indicating the current signal state
    """
    try:
        if not path.exists():
            return SignalType.NONE

        content = path.read_text().strip()
        if content == "ready":
            return SignalType.READY
        elif content == "pause":
            return SignalType.PAUSE
        else:
            return SignalType.NONE
    except (OSError, IOError):
        return SignalType.NONE


def check_signal_file(path: Path) -> bool:
    """Check if the signal file indicates Claude is ready.

    Args:
        path: Path to the signal file

    Returns:
        True if signal file contains "ready", False otherwise
    """
    return read_signal(path) == SignalType.READY


def delete_signal_file(path: Path) -> None:
    """Delete the signal file for cleanup.

    Args:
        path: Path to the signal file
    """
    try:
        if path.exists():
            path.unlink()
    except (OSError, IOError):
        pass  # Ignore errors during cleanup


def create_signal_file(path: Path) -> None:
    """Create an empty signal file to indicate game is running.

    Args:
        path: Path to the signal file
    """
    try:
        path.touch()
    except (OSError, IOError):
        pass  # Ignore errors


# Default lock directory path
LOCK_DIR = Path("/tmp/flappy-claude-lock")


def create_lock_dir(path: Path = LOCK_DIR) -> bool:
    """Create the lock directory to indicate game is running.

    Args:
        path: Path to the lock directory

    Returns:
        True if created successfully, False otherwise
    """
    try:
        path.mkdir(exist_ok=True)
        return True
    except (OSError, IOError):
        return False


def delete_lock_dir(path: Path = LOCK_DIR) -> None:
    """Delete the lock directory during cleanup.

    Args:
        path: Path to the lock directory
    """
    try:
        if path.exists():
            path.rmdir()
    except (OSError, IOError):
        pass  # Ignore errors during cleanup
