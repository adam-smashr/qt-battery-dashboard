from PySide6.QtWidgets import QMainWindow
from ui import main_window


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)  # type: ignore[no-untyped-call]
        self.setup_connections()

    def setup_connections(self) -> None:
        pass
        # self.ui.pushButton_2.clicked.connect(lambda: print(3))
