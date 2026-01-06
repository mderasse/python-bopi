"""Asynchronous Python client for the BoPi API."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .helper import normalize_sensor, require_non_negative, require_range
from .relay import PoolLights, PoolPump, Relay


class SensorHealth(str, Enum):
    """Class to handle Sensors Health."""

    OK = "OK"
    DISCONNECTED = "DISCONNECTED"


@dataclass(frozen=True, slots=True)
class SensorsState:  # pylint: disable=too-many-instance-attributes
    """Class to handle Sensors states of BoPi."""

    temp1: float | None
    temp2: float | None
    boxtemp: float
    boxhumidity: int
    phvalue: float | None
    redoxvalue: int | None
    mode: int
    uptime: int

    lphi: str | None
    tphi: int | None
    lorpi: str | None
    torpi: int | None

    pool_pump: PoolPump
    pool_lights: PoolLights

    relay1: Relay
    relay2: Relay
    relay3: Relay
    relay4: Relay

    @property
    def temp1_health(self) -> SensorHealth:
        """Temperature sensor 1 health status.

        Check if the temperature sensor 1 is healthy

        Args:
        ----
            SensorsState: The current SensorsState object

        Returns:
        -------
            Return a SensorHealth status

        """
        return SensorHealth.DISCONNECTED if self.temp1 is None else SensorHealth.OK

    @property
    def temp2_health(self) -> SensorHealth:
        """Temperature sensor 2 health status.

        Check if the temperature sensor 2 is healthy

        Args:
        ----
            SensorsState: The current SensorsState object

        Returns:
        -------
            Return a SensorHealth status

        """
        return SensorHealth.DISCONNECTED if self.temp2 is None else SensorHealth.OK

    @property
    def ph_health(self) -> SensorHealth:
        """PH Sensort health status.

        Check if the pH sensor is healthy

        Args:
        ----
            SensorsState: The current SensorsState object

        Returns:
        -------
            Return a SensorHealth status

        """
        return SensorHealth.DISCONNECTED if self.phvalue is None else SensorHealth.OK

    @property
    def redox_health(self) -> SensorHealth:
        """Redox sensor 1 health status.

        Check if the Redox sensor is healthy

        Args:
        ----
            SensorsState: The current SensorsState object

        Returns:
        -------
            Return a SensorHealth status

        """
        return SensorHealth.DISCONNECTED if self.redoxvalue is None else SensorHealth.OK

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SensorsState":
        """Construct SensorsState from dict.

        Args:
        ----
            data: A dict containing the sensor data.

        Returns:
        -------
            A SensorsState object with validated data.

        Raises:
        ------
            BoPiValidationError: If data validation fails.
            KeyError: If required keys are missing from data.

        """
        try:
            # Normalize sensors that can be disconnected
            temp1 = normalize_sensor(data.get("temp1", -127))
            temp2 = normalize_sensor(data.get("temp2", -127))
            phvalue = normalize_sensor(data.get("phvalue", -127))
            redoxvalue_normalized = normalize_sensor(data.get("redoxvalue", -127))
            redoxvalue = (
                int(redoxvalue_normalized)
                if redoxvalue_normalized is not None
                else None
            )

            # Validate only if connected
            if phvalue is not None:
                require_range("phvalue", phvalue, 0.0, 14.0)
            if redoxvalue is not None:
                require_range("redoxvalue", redoxvalue, 0, 1000)

            require_range("boxhumidity", data["boxhumidity"], 0, 100)
            require_non_negative("uptime", data["uptime"])

            return cls(
                temp1=temp1,
                temp2=temp2,
                boxtemp=float(data["boxtemp"]),
                boxhumidity=data["boxhumidity"],
                phvalue=phvalue,
                redoxvalue=redoxvalue,
                mode=data["mode"],
                uptime=data["uptime"],
                lphi=data.get("lphi") or None,
                tphi=data.get("tphi"),
                lorpi=data.get("lorpi") or None,
                torpi=data.get("torpi"),
                pool_pump=PoolPump.from_dict(data["poolPump"]),
                pool_lights=PoolLights.from_dict(data["poolLights"]),
                relay1=Relay.from_dict(data["relay1"]),
                relay2=Relay.from_dict(data["relay2"]),
                relay3=Relay.from_dict(data["relay3"]),
                relay4=Relay.from_dict(data["relay4"]),
            )
        except KeyError as e:
            msg = f"Missing required field in sensor data: {e}"
            raise KeyError(msg) from e
        except (ValueError, TypeError) as e:
            msg = f"Invalid data type in sensor data: {e}"
            raise ValueError(msg) from e
