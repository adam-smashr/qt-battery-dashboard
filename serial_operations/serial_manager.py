import serial
import time
from typing import Any
import timeit


class BKPrecision_5492C:
    """docstring for BKPrecision_5492C."""

    def __init__(self, port: str, timeout: float, baudrate: int) -> None:
        self.serial = serial.Serial(port=port, timeout=timeout, baudrate=baudrate)

    def get_voltage(self) -> float:
        try:
            return float(self.query("MEAS:VOLT:DC?"))
        except ValueError:
            return 0.0

    def query(self, cmd: str) -> str:
        self._write_command(cmd)

        return self._read_until_response()

    def _write_command(self, cmd: str) -> None:
        """write serial command to device with newline termination"""
        try:
            self.serial.write(cmd.encode() + b"\n")

        except serial.SerialException as e:
            print(e)

    def _read_until_response(self, max_retries: int = 3, delay: float = 0.05) -> str:
        for _ in range(max_retries):
            response = self.serial.readline()

            decoded = response.decode().strip()

            if decoded and not decoded.startswith("MEAS:"):
                return decoded

            time.sleep(delay)
        return ""


if __name__ == "__main__":
    s = BKPrecision_5492C("com8", 0.5, 19200)

    duration = timeit.timeit(s.get_voltage, number=100)
    print(f"Avg time per call: {duration / 100:.6f}s")

    s._write_command("LOC")
