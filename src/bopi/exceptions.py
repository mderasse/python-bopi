"""Exceptions for BoPi."""

from typing import Any


class BoPiError(Exception):
    """Base exception for BoPi SDK."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        """Initialize BoPiError.

        Args:
        ----
            message: Error message.
            status_code: HTTP status code if applicable.
            response: Response body if applicable.

        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation."""
        if self.status_code:
            return f"{self.message} (Status: {self.status_code})"
        return self.message


class BoPiValidationError(BoPiError):
    """Raised when a value from the sensor is invalid."""


class BoPiConnectionError(BoPiError):
    """Raised when connection/API fails."""


class BoPiTimeoutError(BoPiConnectionError):
    """Raised when a request times out."""


class BoPiConfigError(BoPiError):
    """Raised when configuration is invalid."""
