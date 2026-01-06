"""Asynchronous Python client for the BoPi API."""

from dataclasses import dataclass
from typing import Any

from .helper import require_non_negative


@dataclass(frozen=True, slots=True)
class Relay:
    """Class to handle Relay of BoPi."""

    status: bool
    override: int
    timeleft: int
    role: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relay":
        """Construct Relay from dict.

        Args:
        ----
            data: A dict containing the relay data.

        Returns:
        -------
            A Relay object with validated data.

        Raises:
        ------
            BoPiValidationError: If data validation fails.
            KeyError: If required keys are missing from data.

        """
        try:
            require_non_negative("override", data["override"])
            require_non_negative("timeleft", data["timeleft"])
            return cls(
                status=bool(data["status"]),
                override=data["override"],
                timeleft=data["timeleft"],
                role=data["role"],
            )
        except KeyError as e:
            msg = f"Missing required field in relay data: {e}"
            raise KeyError(msg) from e


@dataclass(frozen=True, slots=True)
class PoolPump:
    """Class to handle Pool Pump of BoPi."""

    status: bool
    override: int
    timeleft: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PoolPump":
        """Construct PoolPump from dict.

        Args:
        ----
            data: A dict containing the pool pump data.

        Returns:
        -------
            A PoolPump object with validated data.

        Raises:
        ------
            BoPiValidationError: If data validation fails.
            KeyError: If required keys are missing from data.

        """
        try:
            require_non_negative("override", data["override"])
            require_non_negative("timeleft", data["timeleft"])
            return cls(
                status=bool(data["status"]),
                override=data["override"],
                timeleft=data["timeleft"],
            )
        except KeyError as e:
            msg = f"Missing required field in pool pump data: {e}"
            raise KeyError(msg) from e


@dataclass(frozen=True, slots=True)
class PoolLights:
    """Class to handle Pool Lights of BoPi."""

    status: bool
    timeleft: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PoolLights":
        """Construct PoolLights from dict.

        Args:
        ----
            data: A dict containing the pool lights data.

        Returns:
        -------
            A PoolLights object with validated data.

        Raises:
        ------
            BoPiValidationError: If data validation fails.
            KeyError: If required keys are missing from data.

        """
        try:
            require_non_negative("timeleft", data["timeleft"])
            return cls(status=bool(data["status"]), timeleft=data["timeleft"])
        except KeyError as e:
            msg = f"Missing required field in pool lights data: {e}"
            raise KeyError(msg) from e
