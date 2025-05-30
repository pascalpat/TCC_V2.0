from datetime import datetime


def parse_date(date_str: str):
    """Parse 'YYYY-MM-DD' into a ``date`` object.

    Raises ``ValueError`` if ``date_str`` is invalid or missing.
    """
    if not date_str:
        raise ValueError("Missing date string")
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_float(value):
    """Return ``float(value)`` or ``None`` if empty."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric value: {value}") from exc


def parse_int(value):
    """Return ``int(value)`` or ``None`` if empty."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid integer value: {value}") from exc


def parse_bool(value):
    """Return ``True``/``False`` for truthy/falsey strings or ``None`` if empty."""
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    str_val = str(value).strip().lower()
    if str_val in {"true", "1", "yes"}:
        return True
    if str_val in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")

__all__ = [
    "parse_date",
    "parse_float",
    "parse_int",
    "parse_bool",
]