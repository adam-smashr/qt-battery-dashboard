from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow
from ui import main_window
from serial_operations.serial_manager import SerialWorker
from utils.type_utilities import VoltageStatistics, BaudRate


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore[no-untyped-call]
        # self.ui.lcdNumber.setSmallDecimalPoint(True)
        self.setup_connections()

    def setup_connections(self) -> None:
        self.worker = SerialWorker("com8", 0.1, BaudRate.BR_115200)
        self.worker.voltage_ready.connect(self.update_lcd)
        self.ui.buttonConnect.clicked.connect(self.handle_connection)

    def handle_connection(self) -> None:
        if not self.worker.running:
            self.worker.start()
            self.ui.buttonConnect.setText("Running")
            self.ui.buttonConnect.setStyleSheet(
                "color: #bbedc6; background-color: #0e6e23"
            )
        else:
            self.worker.stop()
            self.ui.buttonConnect.setText("Stopped")
            self.ui.buttonConnect.setStyleSheet(
                "color: #f0dfaf; background-color: #c28f02"
            )

    @Slot(VoltageStatistics)
    def update_lcd(self, voltage: VoltageStatistics) -> None:
        self.ui.lcdRMS.display(str(voltage.v_rms))
        self.ui.lcdMin.display(str(voltage.v_min))
        self.ui.lcdMax.display(str(voltage.v_max))
