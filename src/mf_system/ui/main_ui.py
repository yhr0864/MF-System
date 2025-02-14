import sys
import time
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
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

from mf_system.logic.controller import Controller


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

        self.init_ui()
        self.controller = None

    def init_ui(self):
        self.setWindowTitle("State Machine")
        self.setGeometry(100, 100, 600, 400)

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

        self.setLayout(layout)

        # Redirect print output to QTextEdit
        sys.stdout = PrintRedirect(self.text_edit)

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
