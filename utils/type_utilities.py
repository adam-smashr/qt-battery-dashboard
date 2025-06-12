from enum import Enum


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
    class for handling output of digitla multimeter.
    rounds given float value to one decimal when created
    implements __str__ to keep # of digits consistent because floats
        leave off trailing zeroes
    """

    precision = 1

    def __new__(cls, value: float) -> "Voltage":
        return super().__new__(cls, round(value, cls.precision))

    def __str__(self) -> str:
        return f"{self:.{self.precision}f}"
