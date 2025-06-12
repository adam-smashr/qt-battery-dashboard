import serial
import time
from PySide6.QtCore import Signal, QThread
from utils.type_utilities import BaudRate, Voltage


class SerialWorker(QThread):
    voltage_ready = Signal(Voltage)

    def __init__(self, port, timeout: float, baudrate: BaudRate) -> None:  # type: ignore
        super().__init__()
        self.device = BKPrecision_5492C(port, timeout, baudrate)
        self.running = True

    def run(self) -> None:
        while self.running:
            voltage = self.device.query_voltage()
            print(voltage)
            self.voltage_ready.emit(voltage)
            self.msleep(10)

    def stop(self) -> None:
        self.running = False
        self.wait()


class BKPrecision_5492C:
    """serial library for BKPrecision_5492C."""

    def __init__(self, port: str, timeout: float, baudrate: BaudRate) -> None:
        """connect to and configure multimeter"""
        print("constructor called")
        self.serial = serial.Serial(port=port, timeout=timeout, baudrate=baudrate.value)

        self._write_command("*RST")
        self._write_command("SENS:VOLT:DC:NPLC 0.01")
        self._write_command("TRIG:SOUR IMM")
        self._write_command("TRIG:COUN 1")
        self._write_command("SAMP:COUN 1")
        self._write_command("INIT")
        time.sleep(3)

    def __del__(self) -> None:
        """clean up"""
        self._write_command("*RST")
        self._write_command("LOC")

    # def __enter__(self) -> "BKPrecision_5492C":
    #     """set up device for measuring voltage"""
    #     self._write_command("*RST")
    #     self._write_command("SENS:VOLT:DC:NPLC 0.01")
    #     self._write_command("TRIG:SOUR IMM")
    #     self._write_command("TRIG:COUN 1")
    #     self._write_command("SAMP:COUN 1")
    #     self._write_command("INIT")
    #     time.sleep(3)

    #     return self

    # def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
    #     """teardown when finished."""
    #     self._write_command("*RST")
    #     self._write_command("LOC")

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
            try:
                split = response.split(b"\r\n")
                decoded = split[-1].decode()
                return decoded
            except UnicodeDecodeError:
                print("Failed to decode response: ", response)
                return ""
        return ""


if __name__ == "__main__":

    dmm = BKPrecision_5492C("com8", 0.1, baudrate=BaudRate.BR_57600)

    # Benchmark
    start = time.perf_counter()
    for _ in range(100):
        voltage = dmm.query_voltage()
        print(voltage)
    end = time.perf_counter()

    print(f"Avg time per call: {(end - start)/100:.6f}s")
