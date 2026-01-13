"""Exceptions for BoPi."""

from typing import Any


class BoPiError(Exception):
    """Base exception for BoPi."""


class BoPiValidationError(BoPiError):
    """Raised when a value from the sensor is invalid."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
    ) -> None:
        """Initialize BoPiValidationError.

        Args:
        ----
            message: Error message.
            field: Field name that failed validation.

        """
        self.message = message
        self.field = field
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation."""
        if self.field:
            return f"{self.message} (Field: {self.field})"
        return self.message


class BoPiConnectionError(BoPiError):
    """Raised when connection/API fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        """Initialize BoPiConnectionError.

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


class BoPiTimeoutError(BoPiConnectionError):
    """Raised when a request times out."""


class BoPiConfigError(BoPiError):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
    ) -> None:
        """Initialize BoPiConfigError.

        Args:
        ----
            message: Error message.
            field: Configuration field that is invalid.

        """
        self.message = message
        self.field = field
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation."""
        if self.field:
            return f"{self.message} (Field: {self.field})"
        return self.message
