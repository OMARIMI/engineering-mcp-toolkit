import pytest

from src.calculations import calculate_current, calculate_power


def test_calculate_current_uses_ohms_law():
    assert calculate_current(12, 6) == 2


def test_calculate_current_rejects_bad_inputs():
    with pytest.raises(ValueError, match="Voltage cannot be negative"):
        calculate_current(-1, 10)

    with pytest.raises(ValueError, match="Resistance must be greater than 0"):
        calculate_current(5, 0)


def test_calculate_power_uses_voltage_times_current():
    assert calculate_power(5, 2) == 10


def test_calculate_power_rejects_bad_inputs():
    with pytest.raises(ValueError, match="Voltage cannot be negative"):
        calculate_power(-5, 2)

    with pytest.raises(ValueError, match="Current cannot be negative"):
        calculate_power(5, -2)
