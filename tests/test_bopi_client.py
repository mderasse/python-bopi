"""Tests for `bopi.bopi_client`."""

import asyncio
from unittest.mock import patch

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from meetbopi import BoPiClient
from meetbopi.exceptions import BoPiConfigError, BoPiConnectionError, BoPiError


async def test_empty_host() -> None:
    """Test host validation."""
    with pytest.raises(BoPiConfigError, match="host must be a non-empty string"):
        BoPiClient("")


async def test_invalid_port() -> None:
    """Test port validation rejects out-of-range values."""
    with pytest.raises(BoPiConfigError, match="port must be between 1 and 65535"):
        BoPiClient("example.com", port=-1)
    with pytest.raises(BoPiConfigError, match="port must be between 1 and 65535"):
        BoPiClient("example.com", port=65536)


async def test_invalid_request_timeout() -> None:
    """Test request timeout validation rejects non-positive values."""
    with pytest.raises(BoPiConfigError, match="request_timeout must be positive"):
        BoPiClient("example.com", request_timeout=-1)
    with pytest.raises(BoPiConfigError, match="request_timeout must be positive"):
        BoPiClient("example.com", request_timeout=0)


async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is parsed correctly."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok", "data": "test"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        response = await bopiclient.request("/")
        assert isinstance(response, dict)
        assert response["status"] == "ok"
        assert response["data"] == "test"
        await bopiclient.close()


async def test_text_request(aresponses: ResponsesMockServer) -> None:
    """Test non JSON response is handled correctly."""
    aresponses.add("example.com", "/", "GET", Response(status=200, text="OK"))
    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        response = await bopiclient.request("/")
        assert response == {"message": "OK"}


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with BoPiClient("example.com") as bopiclient:
        response = await bopiclient.request("/")
        assert response["status"] == "ok"


async def test_post_request(aresponses: ResponsesMockServer) -> None:
    """Test POST requests are handled correctly."""
    aresponses.add("example.com", "/", "POST", Response(status=200, text="OK"))
    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        response = await bopiclient.request("/", method="POST")
        assert response == {"message": "OK"}


async def test_request_port(aresponses: ResponsesMockServer) -> None:
    """Test BoPi API running on non-standard port."""
    aresponses.add(
        "example.com:3333",
        "/",
        "GET",
        Response(text="SUCCESS", status=200),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", port=3333, session=session)
        response = await bopiclient.request("/")
        assert response == {"message": "SUCCESS"}


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from BoPi API."""

    # Faking a timeout by sleeping
    async def response_handler(_: aiohttp.ClientResponse) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return Response(body="Slow!")

    aresponses.add("example.com", "/", "GET", response_handler)

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session, request_timeout=1)
        with pytest.raises(BoPiConnectionError):
            assert await bopiclient.request("/")


async def test_client_error() -> None:
    """Test request client error from BoPi API."""
    # Faking a timeout by sleeping
    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with (
            patch.object(session, "request", side_effect=aiohttp.ClientError),
            pytest.raises(BoPiConnectionError),
        ):
            assert await bopiclient.request("/")


async def test_http_error_404(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 404 response raises BoPiError."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(text="Not Found!", status=404),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with pytest.raises(BoPiError, match="API returned error status 404"):
            await bopiclient.request("/")


async def test_http_error_500(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 500 response raises BoPiError with JSON error info."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(
            body=b'{"status":"nok", "error": "Internal server error"}',
            status=500,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with pytest.raises(BoPiError, match="API returned error status 500"):
            await bopiclient.request("/")


async def test_http_error_invalid_json(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 500 error response with malformed JSON is handled gracefully."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(
            body=b'{"status":"nok}',
            status=500,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with pytest.raises(BoPiError, match="API returned error status 500"):
            await bopiclient.request("/")


async def test_http_success_invalid_json(aresponses: ResponsesMockServer) -> None:
    """Test HTTP 200 response with malformed JSON raises BoPiError."""
    aresponses.add(
        "example.com",
        "/",
        "GET",
        Response(
            body=b'{"status":"nok}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with pytest.raises(BoPiError, match="Failed to parse JSON response"):
            await bopiclient.request("/")


async def test_get_sensors_state_missing_fields(
    aresponses: ResponsesMockServer,
) -> None:
    """Test get_sensors_state raises KeyError for missing required fields."""
    aresponses.add(
        "example.com",
        "/allsensorsv2",
        "GET",
        Response(
            body=b'{"status":"nok"}',
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        bopiclient = BoPiClient("example.com", session=session)
        with pytest.raises(KeyError, match="Missing required field in sensor data"):
            await bopiclient.get_sensors_state()
