import serial
import time
from typing import Any, Self
import timeit
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


class BKPrecision_5492C:
    """serial library for BKPrecision_5492C."""

    def __init__(self, port: str, timeout: float, baudrate: BaudRate) -> None:
        self.serial = serial.Serial(port=port, timeout=timeout, baudrate=baudrate.value)

    def __enter__(self) -> Self:
        """set up device for measuring voltage"""
        self._write_command("*RST")
        self._write_command("SENS:VOLT:DC:NPLC 0.01")
        self._write_command("TRIG:SOUR IMM")
        self._write_command("TRIG:COUN 1")
        self._write_command("SAMP:COUN 1")
        self._write_command("INIT")
        time.sleep(3)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """teardown when finished."""
        self._write_command("*RST")
        self._write_command("LOC")

    def query_voltage(self) -> Voltage:
        """return value from the stream of data & return zero if it doesn't exist"""
        self._write_command("INIT")
        try:
            raw_data = float(self.query("FETCh?"))
            return Voltage(raw_data)
        except ValueError:
            return Voltage(0.0)

    def query(self, cmd: str) -> str:
        self._write_command(cmd)
        return self.read_value()

    def _write_command(self, cmd: str) -> None:
        """write serial command to device with newline termination"""
        try:
            self.serial.write(cmd.encode() + b"\n")
        except serial.SerialException as e:
            print(e)

    def read_value(self) -> str:
        """
        read all of the lines and return the last one which has the voltage.
        if it's not there, then return an empty string
        """
        response = self.serial.read_until(b"").strip()
        if response:
            split = response.split(b"\r\n")
            decoded = split[-1].decode()
            return decoded
        return ""


if __name__ == "__main__":
    with BKPrecision_5492C("com8", 0.1, baudrate=BaudRate.BR_57600) as dmm:

        # Benchmark
        start = time.perf_counter()
        for _ in range(100):
            voltage = dmm.query_voltage()
            print(voltage)
        end = time.perf_counter()

        print(f"Avg time per call: {(end - start)/100:.6f}s")
