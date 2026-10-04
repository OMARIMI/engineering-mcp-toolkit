def calculate_current(
    voltage: float,
    resistance: float,
) -> float:
    """Calculate current in amps using Ohm's law."""

    if voltage < 0:
        raise ValueError(
            "Voltage cannot be negative."
        )

    if resistance <= 0:
        raise ValueError(
            "Resistance must be greater than 0."
        )

    return voltage / resistance


def calculate_power(
    voltage: float,
    current: float,
) -> float:
    """Calculate electrical power in watts."""

    if voltage < 0:
        raise ValueError(
            "Voltage cannot be negative."
        )

    if current < 0:
        raise ValueError(
            "Current cannot be negative."
        )

    return voltage * current