"""Environment variable parsing helpers."""

import os


def get_env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment value."""
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_env_str(name: str, default: str) -> str:
    """Read a string environment value."""
    value = os.getenv(name, default).strip()
    return value or default


def get_env_list(name: str, default: str) -> tuple[str, ...]:
    """Read a comma-separated environment value, omitting empty entries."""
    values = tuple(value.strip() for value in os.getenv(name, default).split(","))
    return tuple(value for value in values if value) or (default,)


def get_env_int(name: str, default: int) -> int:
    """Read an integer environment value."""
    return int(os.getenv(name, str(default)))
