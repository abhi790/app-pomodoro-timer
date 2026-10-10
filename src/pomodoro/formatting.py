"""Small helpers that turn numbers into text for the screen."""


def format_clock(seconds: int) -> str:
    """Turn a number of seconds into ``MM:SS`` (for example 1500 -> "25:00")."""
    minutes, secs = divmod(max(0, int(seconds)), 60)
    return f"{minutes:02d}:{secs:02d}"
