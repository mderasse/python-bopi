"""Asynchronous Python client for the BoPi API."""

from .exceptions import BoPiValidationError


def require_range(name: str, value: float, min_v: float, max_v: float) -> None:
    """Validate value range.

    Validate that a value is in a given range.

    Args:
    ----
        name: Name of the value.
        value: Current value.
        min_v: Minimum authorized value.
        max_v: Maximum authorized value.

    Raises:
    ------
        BoPiValidationError: If validation fails.

    """
    if not isinstance(value, (int, float)):
        msg = f"{name} must be a number, got {type(value).__name__}"
        raise BoPiValidationError(msg, field=name)

    if not (min_v <= value <= max_v):
        msg = f"{name} out of range: {value} (expected {min_v}-{max_v})"
        raise BoPiValidationError(msg, field=name)


def require_non_negative(name: str, value: int) -> None:
    """Validate value is non-negative.

    Validate that a value is only non-negative.

    Args:
    ----
        name: Name of the value.
        value: Current value.

    Raises:
    ------
        BoPiValidationError: If validation fails.

    """
    if not isinstance(value, int):
        msg = f"{name} must be an integer, got {type(value).__name__}"
        raise BoPiValidationError(msg, field=name)

    if value < 0:
        msg = f"{name} must be >= 0, got {value}"
        raise BoPiValidationError(msg, field=name)


def normalize_sensor(value: float | int) -> float | None:
    """Normalize Sensor.

    Check if sensor is not available (-127) and return None instead.

    Args:
    ----
        value: Sensor value.

    Returns:
    -------
        The value or None if sensor is not available.

    """
    if not isinstance(value, (int, float)):
        return None

    # Check for disconnected sensor value
    if value == -127:
        return None

    return float(value)
