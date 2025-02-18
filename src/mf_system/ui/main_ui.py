import sys
import time
from pymongo import MongoClient
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QGroupBox,
    QGridLayout,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QTabWidget,
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

from mf_system.logic.controller import Controller

_pump_init_para = {
    "pump1": {
        "name": "Nemesys_M_1_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 14.70520755382068,
        "max_piston_stroke_mm": 60,
    },
    "pump2": {
        "name": "Nemesys_M_2_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 14.70520755382068,
        "max_piston_stroke_mm": 60,
    },
    "pump3": {
        "name": "Nemesys_M_3_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 32.80671055737278,
        "max_piston_stroke_mm": 60,
    },
    "pump4": {
        "name": "Nemesys_M_4_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 32.80671055737278,
        "max_piston_stroke_mm": 60,
    },
    "pump5": {
        "name": "Nemesys_M_5_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 23.207658393177034,
        "max_piston_stroke_mm": 60,
    },
    "pump6": {
        "name": "Nemesys_M_6_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 23.207658393177034,
        "max_piston_stroke_mm": 60,
    },
    "pump7": {
        "name": "Nemesys_M_7_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 23.207658393177034,
        "max_piston_stroke_mm": 60,
    },
    "pump8": {
        "name": "Nemesys_M_8_Pump",
        "pressure_limit": 10,
        "inner_diameter_mm": 10.40522314849599,
        "max_piston_stroke_mm": 60,
    },
}


class PrintRedirect:
    """Redirects print statements to QTextEdit"""

    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text)  # Append text to QTextEdit
        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)  # Move cursor to end

    def flush(self):
        pass  # Needed for compatibility with sys.stdout


class ExperimentThread(QThread):
    """Runs the experiment in a separate thread"""

    finished = pyqtSignal()  # Signal when experiment is done

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        self.controller.run_experiment()  # Run the experiment
        self.finished.emit()  # Emit signal when done


class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        # MongoDB Connection
        client = MongoClient("mongodb://localhost:27017/")
        db = client["experiment_db"]
        samples_collection = db["sample_config"]
        hardware_collection = db["hardware_config"]
        measure_collection = db["measurements"]

        self.hw_config = hardware_collection.find_one()

        self.init_ui()
        self.controller = None

    def init_ui(self):
        self.setWindowTitle("MF-System")
        self.setGeometry(100, 100, 1200, 800)

        self.create_hardware_group_box()
        self.create_state_machine_group_box()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.hw_group_box, 1, 0)
        mainLayout.addWidget(self.sm_group_box, 1, 1)

        self.setLayout(mainLayout)

    def create_state_machine_group_box(self):

        self.sm_group_box = QGroupBox("2. State Machine Setup")

        layout = QVBoxLayout()

        # Radio Buttons
        self.button_group = QButtonGroup(self)

        self.radioButton1 = QRadioButton("Dispense Only")
        self.radioButton2 = QRadioButton("Measure Only")
        self.radioButton3 = QRadioButton("Both")
        self.radioButton1.setChecked(True)
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)
        layout.addWidget(self.radioButton3)

        self.button_group.addButton(self.radioButton1)
        self.button_group.addButton(self.radioButton2)
        self.button_group.addButton(self.radioButton3)

        # Display Window
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.text_edit)

        self.label = QLabel("Click start to start")
        layout.addWidget(self.label)

        # Create Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)  # Start at 0%
        self.progress_bar.setVisible(False)  # Hide initially
        layout.addWidget(self.progress_bar)

        # Push Button "Start"
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_state_machine)
        layout.addWidget(self.start_button)

        # Push Button "Stop"
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_state_machine)
        layout.addWidget(self.stop_button)

        self.sm_group_box.setLayout(layout)

        # Redirect print output to QTextEdit
        sys.stdout = PrintRedirect(self.text_edit)

    def create_hardware_group_box(self):
        self.hw_group_box = QGroupBox("1. Hardware Setup")

        # Arduino Layout Box
        arduino_layout = QVBoxLayout()
        formLayout = QFormLayout()

        self.port_arduino = QLineEdit("COM14", parent=self.hw_group_box)
        self.baudrate_arduino = QLineEdit("9600", parent=self.hw_group_box)
        self.timeout_arduino = QLineEdit("0.5", parent=self.hw_group_box)
        dropdown = QComboBox()
        dropdown.addItems(["9600", "115200"])
        dropdown.currentTextChanged.connect(self.baudrate_arduino.setText)

        baudrate_layout = QHBoxLayout()
        baudrate_layout.addWidget(self.baudrate_arduino)
        baudrate_layout.addWidget(dropdown)

        formLayout.addRow("Port:", self.port_arduino)
        formLayout.addRow("Baudrate:", baudrate_layout)
        formLayout.addRow("Timeout:", self.timeout_arduino)

        arduino_layout.addLayout(formLayout)

        arduino_box = QGroupBox("Arduino Setup")
        arduino_box.setLayout(arduino_layout)

        # DLS Layout Box
        dls_layout = QVBoxLayout()
        formLayout_dls = QFormLayout()

        self.port_dls = QLineEdit("COM7", parent=self.hw_group_box)
        self.baudrate_dls = QLineEdit("9600", parent=self.hw_group_box)
        self.timeout_dls = QLineEdit("1", parent=self.hw_group_box)

        dropdown_dls = QComboBox()
        dropdown_dls.addItems(["9600", "115200"])
        dropdown_dls.currentTextChanged.connect(self.baudrate_dls.setText)

        baudrate_layout_dls = QHBoxLayout()
        baudrate_layout_dls.addWidget(self.baudrate_dls)
        baudrate_layout_dls.addWidget(dropdown_dls)

        formLayout_dls.addRow("Port:", self.port_dls)
        formLayout_dls.addRow("Baudrate:", baudrate_layout_dls)
        formLayout_dls.addRow("Timeout:", self.timeout_dls)

        dls_layout.addLayout(formLayout_dls)

        dls_box = QGroupBox("DLS Setup")
        dls_box.setLayout(dls_layout)

        # Gantry Layout Box
        gantry_layout = QVBoxLayout()
        formLayout_gantry = QFormLayout()

        self.ip_gantry = QLineEdit("192.168.0.0", parent=self.hw_group_box)
        self.port_gantry = QLineEdit("0000", parent=self.hw_group_box)

        formLayout_gantry.addRow("IP:", self.ip_gantry)
        formLayout_gantry.addRow("Port:", self.port_gantry)

        gantry_layout.addLayout(formLayout_gantry)

        gantry_box = QGroupBox("Gantry Setup")
        gantry_box.setLayout(gantry_layout)

        # UV Layout Box
        uv_layout = QVBoxLayout()

        uv_box = QGroupBox("UV Setup")
        uv_box.setLayout(uv_layout)

        # Pump Layout Box
        pump_layout = QVBoxLayout()

        self.pump_tab = QTabWidget()

        for key, value in _pump_init_para.items():
            self.create_pump_tabs(key, value)

        pump_layout.addWidget(self.pump_tab)
        pump_box = QGroupBox("Pumps Setup")
        pump_box.setLayout(pump_layout)

        # Add layout boxes for arduino, pump, dls, uv...
        layout = QVBoxLayout()
        layout.addWidget(arduino_box)
        layout.addWidget(dls_box)
        layout.addWidget(gantry_box)
        layout.addWidget(uv_box)
        layout.addWidget(pump_box)
        self.save_button = QPushButton("Save to Database")
        self.result_label = QLabel("Status: Waiting for input...", self.hw_group_box)
        layout.addWidget(self.save_button)
        layout.addWidget(self.result_label)
        self.hw_group_box.setLayout(layout)

        # Connect the button click event
        self.save_button.clicked.connect(self.save_data)

    def save_data(self):
        doc = {
            "Arduino": {
                "port": self.port_arduino.text(),
                "baudrate": self.baudrate_arduino.text(),
                "timeout": self.timeout_arduino.text(),
            },
            "DLS": {
                "port": self.port_dls.text(),
                "baudrate": self.baudrate_dls.text(),
                "timeout": self.timeout_dls.text(),
            },
            "Gantry": {"ip": self.ip_gantry.text(), "port": self.port_gantry.text()},
        }
        self.hardware_collection.insert_one(doc)
        self.result_label.setText("Status: Data saved successfully!")

    def create_pump_tabs(self, tab_name: str, init_dict: dict):
        tab = QWidget()
        tab_box = QFormLayout()

        name = QLineEdit(init_dict["name"])
        name.setReadOnly(True)
        name.setStyleSheet("color: gray; background-color: #f0f0f0;")
        pressure_limit = QLineEdit(str(init_dict["pressure_limit"]))
        pressure_limit.setReadOnly(True)
        pressure_limit.setStyleSheet("color: gray; background-color: #f0f0f0;")
        inner_diameter = QLineEdit(str(init_dict["inner_diameter_mm"]))
        inner_diameter.setReadOnly(True)
        inner_diameter.setStyleSheet("color: gray; background-color: #f0f0f0;")
        max_piston_stroke = QLineEdit(str(init_dict["max_piston_stroke_mm"]))
        max_piston_stroke.setReadOnly(True)
        max_piston_stroke.setStyleSheet("color: gray; background-color: #f0f0f0;")
        tab_box.addRow("name:", name)
        tab_box.addRow("pressure_limit:", pressure_limit)
        tab_box.addRow("inner_diameter_mm:", inner_diameter)
        tab_box.addRow("max_piston_stroke_mm:", max_piston_stroke)
        tab.setLayout(tab_box)

        self.pump_tab.addTab(tab, tab_name)

    def start_state_machine(self):
        # Disable Start button
        self.start_button.setEnabled(False)
        self.label.setText("Status: Running")
        print("start exp")

        # Get selected radio button text
        selected_button = self.button_group.checkedButton()
        selected_option = selected_button.text()
        print(f"Selected Mode: {selected_option}")

        # Initialize controller with the selected option
        self.controller = Controller(user_input=selected_option)

        # # Ensure the thread persists
        # if hasattr(self, "experiment_thread") and self.experiment_thread.isRunning():
        #     print("Experiment already running.")
        #     return  # Avoid starting multiple threads

        # Run experiment in a separate thread
        self.experiment_thread = ExperimentThread(self.controller)
        self.progress_bar.setVisible(True)  # Show progress bar
        self.experiment_thread.finished.connect(self.progress_bar.setValue)
        self.experiment_thread.finished.connect(self.on_experiment_finished)
        self.experiment_thread.start()

    def on_experiment_finished(self):
        """Handle experiment completion"""

        self.label.setText("Completed")

        # Re-enable the Start button after experiment finishes
        self.start_button.setEnabled(True)

        # Ensure the thread is cleaned up properly
        if hasattr(self, "experiment_thread"):
            self.experiment_thread.deleteLater()  # Mark for deletion
            self.experiment_thread = None  # Remove reference

    def stop_state_machine(self):
        self.label.setText("Stopped")
        # self.controller.pump.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
