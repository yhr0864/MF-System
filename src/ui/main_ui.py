import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from logic.controller import Controller


class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = Controller()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pump Control")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Pump Status: Stopped")
        layout.addWidget(self.label)

        self.start_button = QPushButton("Start Pump")
        self.start_button.clicked.connect(self.start_pump)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Pump")
        self.stop_button.clicked.connect(self.stop_pump)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def start_pump(self):
        self.controller.run_process()
        self.label.setText("Pump Status: Running")

    def stop_pump(self):
        self.controller.pump.stop()
        self.label.setText("Pump Status: Stopped")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
