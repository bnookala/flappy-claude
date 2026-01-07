"""Inter-process communication via signal files."""

from pathlib import Path


def check_signal_file(path: Path) -> bool:
    """Check if the signal file indicates Claude is ready.

    Args:
        path: Path to the signal file

    Returns:
        True if signal file contains "ready", False otherwise
    """
    try:
        if not path.exists():
            return False

        content = path.read_text().strip()
        return content == "ready"
    except (OSError, IOError):
        return False


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
