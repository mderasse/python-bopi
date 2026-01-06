"""Tests for `bopi.helper`."""

import pytest

from bopi.helper import normalize_sensor, require_non_negative, require_range
from bopi.exceptions import BoPiValidationError


class TestNormalizeSensor:
    """Tests for normalize_sensor function."""

    def test_normalize_sensor_valid_value(self) -> None:
        """Test normalize_sensor returns valid sensor value."""
        result = normalize_sensor(25.5)
        assert result == 25.5

    def test_normalize_sensor_zero(self) -> None:
        """Test normalize_sensor with zero value."""
        result = normalize_sensor(0)
        assert result == 0

    def test_normalize_sensor_negative_value(self) -> None:
        """Test normalize_sensor with negative value."""
        result = normalize_sensor(-10.5)
        assert result == -10.5

    def test_normalize_sensor_disconnected_value(self) -> None:
        """Test normalize_sensor returns None for disconnected sensor (-127)."""
        result = normalize_sensor(-127)
        assert result is None

    def test_normalize_sensor_integer(self) -> None:
        """Test normalize_sensor with integer value."""
        result = normalize_sensor(50)
        assert result == 50

    def test_normalize_sensor_float(self) -> None:
        """Test normalize_sensor with float value."""
        result = normalize_sensor(50.75)
        assert result == 50.75


class TestRequireNonNegative:
    """Tests for require_non_negative function."""

    def test_require_non_negative_valid_value(self) -> None:
        """Test require_non_negative with valid non-negative value."""
        # Should not raise
        require_non_negative("uptime", 100)

    def test_require_non_negative_zero(self) -> None:
        """Test require_non_negative with zero value."""
        # Should not raise
        require_non_negative("count", 0)

    def test_require_non_negative_large_value(self) -> None:
        """Test require_non_negative with large value."""
        # Should not raise
        require_non_negative("uptime", 1000000)

    def test_require_non_negative_negative_value(self) -> None:
        """Test require_non_negative raises on negative value."""
        with pytest.raises(BoPiValidationError):
            require_non_negative("uptime", -1)


class TestRequireRange:
    """Tests for require_range function."""

    def test_require_range_valid_value_in_range(self) -> None:
        """Test require_range with valid value in range."""
        # Should not raise
        require_range("phvalue", 7.0, 0.0, 14.0)

    def test_require_range_lower_boundary(self) -> None:
        """Test require_range with value at lower boundary."""
        # Should not raise
        require_range("phvalue", 0.0, 0.0, 14.0)

    def test_require_range_upper_boundary(self) -> None:
        """Test require_range with value at upper boundary."""
        # Should not raise
        require_range("phvalue", 14.0, 0.0, 14.0)

    def test_require_range_integer_values(self) -> None:
        """Test require_range with integer values."""
        # Should not raise
        require_range("redoxvalue", 500, 0, 1000)

    def test_require_range_below_minimum(self) -> None:
        """Test require_range raises when value is below minimum."""
        with pytest.raises(BoPiValidationError):
            require_range("phvalue", -1.0, 0.0, 14.0)

    def test_require_range_above_maximum(self) -> None:
        """Test require_range raises when value is above maximum."""
        with pytest.raises(BoPiValidationError):
            require_range("phvalue", 15.0, 0.0, 14.0)

    def test_require_range_humidity(self) -> None:
        """Test require_range with humidity percentage."""
        # Should not raise
        require_range("boxhumidity", 50, 0, 100)

    def test_require_range_humidity_boundary(self) -> None:
        """Test require_range with humidity at boundary."""
        with pytest.raises(BoPiValidationError):
            require_range("boxhumidity", 101, 0, 100)

    def test_require_range_redox(self) -> None:
        """Test require_range with redox value."""
        # Should not raise
        require_range("redoxvalue", 300, 0, 1000)

    def test_require_range_redox_invalid(self) -> None:
        """Test require_range with invalid redox value."""
        with pytest.raises(BoPiValidationError):
            require_range("redoxvalue", 1001, 0, 1000)
