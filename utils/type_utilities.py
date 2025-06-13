from enum import Enum
from dataclasses import dataclass


class BaudRate(Enum):
    """BaudRates used by BK Precision 5492C"""

    BR_4800 = 4800
    BR_9600 = 9600
    BR_19200 = 19200
    BR_38400 = 38400
    BR_57600 = 57600
    BR_115200 = 115200


class Voltage(float):
    """
    A float subclass representing a voltage value with fixed decimal precision.
    Attributes:
        precision (int): Number of decimal places to round the voltage value to
            (default is 1).
    Methods:
        __new__(cls, value: float) -> "Voltage":
            Creates a new Voltage instance, rounding the value to the specified
                precision.
        __str__(self) -> str:
            Returns the string representation of the voltage, formatted to the
                specified precision.
    """

    precision = 1

    def __new__(cls, value: float) -> "Voltage":
        return super().__new__(cls, round(value, cls.precision))

    def __str__(self) -> str:
        return f"{self:.{self.precision}f}"


@dataclass
class VoltageStatistics:
    """
    Class for tracking and updating voltage statistics, including RMS, maximum, and
        minimum values.
    Attributes:
        v_rms (Voltage): The root mean square voltage value.
        v_max (Voltage): The maximum voltage observed.
        v_min (Voltage): The minimum voltage observed.
    Methods:
        reset():
            Resets the maximum and minimum voltages to the current RMS voltage.
        calculate_min_max():
            Updates the maximum and minimum voltages based on the current RMS voltage.
    """

    v_rms: Voltage = Voltage(0.0)
    v_max: Voltage = Voltage(0.0)
    v_min: Voltage = Voltage(0.0)

    def reset(self) -> None:
        self.v_max = self.v_rms
        self.v_min = self.v_rms

    def calculate_min_max(self) -> None:
        self.v_max = max(self.v_rms, self.v_max)
        self.v_min = min(self.v_rms, self.v_min)
