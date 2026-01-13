"""Asynchronous Python client for the BoPi API."""

from __future__ import annotations

import asyncio
import json
import socket
from typing import TYPE_CHECKING, Any, Self

import aiohttp
from yarl import URL

from .sensors_state import SensorsState
from .exceptions import (
    BoPiConnectionError,
    BoPiError,
    BoPiTimeoutError,
    BoPiConfigError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


# pylint: disable=too-many-instance-attributes
class BoPiClient:
    """Main class for handling connections with BoPi.

    Provides a robust client for communicating with the BoPi API with features like:
    - Connection pooling and session management
    - Comprehensive error handling
    - Request timeout support
    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        host: str,
        *,
        port: int = 80,
        timeout: int = 30,
        session: aiohttp.client.ClientSession | None = None,
    ) -> None:
        """Initialize connection with BoPi.

        Class constructor for setting up an BoPi object to
        communicate with an BoPi API.

        Args:
        ----
            host: Hostname or IP address of the BoPi API.
            port: Port on which the API runs, usually 80 or 3000.
            timeout: Max timeout to wait for a response from the API in seconds.
            session: Optional, shared, aiohttp client session.

        Raises:
        ------
            BoPiConfigError: If host is invalid or port is out of range.

        """
        # Validate inputs
        if not host or not isinstance(host, str):
            msg = "host must be a non-empty string"
            raise BoPiConfigError(msg, field="host")
        if not 1 <= port <= 65535:
            msg = f"port must be between 1 and 65535, got {port}"
            raise BoPiConfigError(msg, field="port")
        if timeout <= 0:
            msg = f"timeout must be positive, got {timeout}"
            raise BoPiConfigError(msg, field="timeout")

        self._session = session
        self._close_session = False

        self.host = host
        self.port = port
        self.timeout = timeout
        self.sensors_state: SensorsState | None = None  # cached sensor state

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    async def request(
        self,
        uri: str,
        method: str = "GET",
        data: Any | None = None,
        json_data: dict[str, Any] | None = None,
        params: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to the BoPi API.

        Make a request against the BoPi API and handles the response.

        Args:
        ----
            uri: The request URI on the BoPi API to call.
            method: HTTP method to use for the request; e.g., GET, POST.
            data: RAW HTTP request data to send with the request.
            json_data: Dictionary of data to send as JSON with the request.
            params: Mapping of request parameters to send with the request.

        Returns:
        -------
            The response from the API. In case the response is a JSON response,
            the method will return a decoded JSON response as a Python
            dictionary. In other cases, it will return the RAW text response.

        Raises:
        ------
            BoPiTimeoutError: Request timed out.
            BoPiConnectionError: An error occurred while communicating
                with the BoPi API (connection issues).
            BoPiError: An error occurred while processing the
                response from the BoPi API (invalid data).

        """
        url = URL.build(scheme="http", host=self.host, port=self.port, path="/").join(
            URL(uri)
        )

        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        skip_auto_headers = None
        if data is None and json_data is None:
            skip_auto_headers = {"Content-Type"}

        try:
            async with asyncio.timeout(self.timeout):
                response = await self._session.request(
                    method,
                    url,
                    data=data,
                    json=json_data,
                    params=params,
                    headers=headers,
                    skip_auto_headers=skip_auto_headers,
                )

            return await self._handle_response(response)

        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to BoPi API."
            raise BoPiTimeoutError(msg, status_code=None, response=None) from exception
        except (aiohttp.ClientConnectorError, socket.gaierror) as exception:
            raise BoPiConnectionError(
                f"Error occurred while communicating with BoPi: {exception}",
                status_code=None,
                response=None,
            ) from exception
        except aiohttp.ClientError as exception:
            raise BoPiConnectionError(
                f"Error occurred while communicating with BoPi: {exception}",
                status_code=None,
                response=None,
            ) from exception

    async def _handle_response(
        self, response: aiohttp.ClientResponse
    ) -> dict[str, Any]:
        """Handle API response.

        Args:
        ----
            response: The response from the API.

        Returns:
        -------
            The parsed response.

        Raises:
        ------
            BoPiError: If the response indicates an error.

        """
        content_type = response.headers.get("Content-Type", "")

        if response.status // 100 in [4, 5]:
            contents = await response.read()
            response.close()

            error_data = None
            try:
                if content_type == "application/json":
                    error_data = json.loads(contents.decode("utf8"))
                else:
                    error_data = {"message": contents.decode("utf8")}
            except (json.JSONDecodeError, UnicodeDecodeError):
                error_data = {"message": "Unknown error"}

            msg = f"API returned error status {response.status}"
            raise BoPiConnectionError(
                msg, status_code=response.status, response=error_data
            )

        if "application/json" in content_type:
            try:
                return await response.json()
            except json.JSONDecodeError as e:
                msg = f"Failed to parse JSON response: {e}"
                raise BoPiError(msg) from e

        text = await response.text()
        return {"message": text}

    async def close(self) -> None:
        """Close open client session.

        Safely closes the internal session if one was created.
        Does nothing if a session was provided during initialization.
        """
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The BoPiClient object.

        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async exit.

        Ensures the session is closed even if an exception occurred.

        Args:
        ----
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Exception traceback.

        """
        await self.close()

    async def get_sensors_state(self) -> SensorsState:
        """Return BoPi Sensors State.

        Fetches and caches the current state of all sensors from the BoPi API.

        Returns
        -------
            A SensorsState object containing all sensor readings.

        Raises:
        ------
            BoPiConnectionError: If unable to connect to the API.
            BoPiError: If the API returns an error or invalid data.

        """
        response = await self.request("allsensorsv2")
        self.sensors_state = SensorsState.from_dict(response)
        return self.sensors_state
