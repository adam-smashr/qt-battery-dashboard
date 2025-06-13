import serial
import time
from PySide6.QtCore import Signal, QThread
from utils.type_utilities import BaudRate, Voltage, VoltageStatistics


class MultimeterException(Exception):
    """Exception raised for errors with multimeter communication"""

    def __init__(self, message: str, original_exception: Exception):
        super().__init__(f"Multimeter Error: {message}")
        self.original_exception = original_exception


class SerialWorker(QThread):
    voltage_ready = Signal(VoltageStatistics)

    def __init__(self, port: str, timeout: float, baudrate: BaudRate) -> None:
        super().__init__()
        self.device = BKPrecision_5492C(port, timeout, baudrate)
        self.running = False

    def run(self) -> None:
        """
        Continuously updates and emits device voltage readings while running.

        This method starts a loop that repeatedly updates the device's voltage readings,
        resets the voltage data on the first iteration, prints the current voltages,
        emits a signal with the updated voltages, and then sleeps
            briefly before repeating.
        The loop continues until `self.running` is set to False.

        Emits:
            voltage_ready (signal): Emitted with the updated voltage readings.
        """
        self.running = True
        first_time = True
        while self.running:
            self.device.update_voltages()
            if first_time:
                self.device.voltages.reset()
                first_time = False
            print(self.device.voltages)
            self.voltage_ready.emit(self.device.voltages)
            self.msleep(10)

    def stop(self) -> None:
        self.running = False
        self.device.close()
        self.wait()


class BKPrecision_5492C:
    """serial library for BKPrecision_5492C."""

    def __init__(self, port: str, timeout: float, baudrate: BaudRate) -> None:
        """
        Initializes the SerialManager instance by setting up the serial connection
            and configuring the device.
        Args:
            port (str): The serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0').
            timeout (float): The timeout value for serial communication in seconds.
            baudrate (BaudRate): The baud rate for the serial connection.
        Side Effects:
            - Initializes a VoltageStatistics instance.
            - Opens a serial connection with the specified parameters.
            - Sends a startup sequence of commands to the connected device.
            - Waits for 3 seconds after sending the startup sequence.
        """

        print("constructor called")
        self.voltages = VoltageStatistics()
        self.serial = serial.Serial(port=port, timeout=timeout, baudrate=baudrate.value)
        startup_sequence = [
            "*RST",
            "SENS:VOLT:DC:NPLC 0.01",
            "TRIG:SOUR IMM",
            "TRIG:COUN 1",
            "SAMP:COUN 1",
            "INIT",
        ]
        for command in startup_sequence:
            self._write_command(command)
        time.sleep(3)

    def close(self) -> None:
        """clean up"""
        self._write_command("*RST")
        self._write_command("LOC")

    def update_voltages(self) -> None:
        """update v_rms, v_min, and v_max"""
        self.voltages.v_rms = self.query_voltage()
        self.voltages.calculate_min_max()

    def query_voltage(self) -> Voltage:
        """
        Queries the device for the current voltage measurement.

        Sends an initialization command followed by a fetch command to
            retrieve the voltage value.
        If the response cannot be converted to a float, returns a Voltage object
            with a value of 0.0.

        Returns:
            Voltage: The measured voltage value, or 0.0 if parsing fails.
        """
        self._write_command("INIT")
        try:
            raw_data = float(self.query("FETCh?"))
            return Voltage(raw_data)
        except ValueError:
            return Voltage(0.0)

    def query(self, cmd: str) -> str:
        """
        Sends a command to the serial device and returns the response as a string.

        Args:
            cmd (str): The command string to send to the device.

        Returns:
            str: The response received from the device.

        Raises:
            MultimeterException: If a serial communication error, decoding error, or
                value error occurs during the query.
        """
        try:
            self._write_command(cmd)
            return self.read_value()
        except (serial.SerialException, UnicodeDecodeError, ValueError) as e:
            raise MultimeterException("failed during query()", e)

    def _write_command(self, cmd: str) -> None:
        """Write serial command to device with newline termination"""
        try:
            self.serial.write(cmd.encode() + b"\n")
        except (serial.SerialException, UnicodeEncodeError, ValueError) as e:
            raise MultimeterException("failed during _write_command()", e)

    def read_value(self) -> str:
        """
        Reads a value from the serial connection until a termination sequence is
            encountered.

        Returns:
            str: The decoded string value read from the serial port. Returns an empty
                string if no response is received.

        Raises:
            MultimeterException: If a serial communication error, decoding error, or
                value error occurs during reading.
        """
        try:
            response = self.serial.read_until(b"").strip()
            if response:
                split = response.split(b"\r\n")
                decoded = split[-1].decode()
                return decoded
            return ""
        except (serial.SerialException, UnicodeDecodeError, ValueError) as e:
            raise MultimeterException("failed during read_value()", e)


if __name__ == "__main__":

    dmm = BKPrecision_5492C("com8", 0.1, baudrate=BaudRate.BR_57600)

    # Benchmark
    start = time.perf_counter()
    for _ in range(100):
        voltage = dmm.query_voltage()
        print(voltage)
    end = time.perf_counter()

    print(f"Avg time per call: {(end - start)/100:.6f}s")
