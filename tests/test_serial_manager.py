import unittest
from unittest.mock import MagicMock
from serial_operations.serial_manager import BKPrecision_5492C


class TestBKPrecisionReadValue(unittest.TestCase):
    def setUp(self) -> None:
        # Create instance without calling __init__
        self.device = BKPrecision_5492C.__new__(BKPrecision_5492C)
        self.device.serial = MagicMock()

    def test_read_value_returns_last_line(self) -> None:
        # Simulate serial.read_until returning multiple lines
        self.device.serial.read_until.return_value = (  # type: ignore[attr-defined]
            b"123\r\n456\r\n789\r\n"
        )
        result = self.device.read_value()
        self.assertEqual(result, "789")

    def test_read_value_returns_empty_string(self) -> None:
        # Simulate serial.read_until returning empty bytes
        self.device.serial.read_until.return_value = b""  # type: ignore[attr-defined]
        result = self.device.read_value()
        self.assertEqual(result, "")

    def test_read_value_handles_single_line(self) -> None:
        self.device.serial.read_until.return_value = (  # type: ignore[attr-defined]
            b"42\r\n"
        )
        result = self.device.read_value()
        self.assertEqual(result, "42")


if __name__ == "__main__":
    unittest.main()
