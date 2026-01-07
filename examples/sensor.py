"""Asynchronous Python client for the BoPi API."""

import asyncio

from meetbopi import BoPiClient


async def main() -> None:
    """Show example how to get status of your BoPi API."""
    async with BoPiClient(host="192.168.87.26") as bopi:
        sensorstate = await bopi.get_sensors_state()
        print("Ph Value:", sensorstate.phvalue)


if __name__ == "__main__":
    asyncio.run(main())
