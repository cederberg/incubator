import os

_EXT_MAP: dict[str, str] = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".mdown": "markdown",
    ".mkd": "markdown",
    ".txt": "markdown",
    ".text": "markdown",
}


def detect_syntax(filename: str) -> str | None:
    """Return syntax name from file extension, or None if unknown."""
    _, ext = os.path.splitext(filename.lower())
    return _EXT_MAP.get(ext)
