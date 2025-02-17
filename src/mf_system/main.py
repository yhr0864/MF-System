import sys
from mf_system.ui.main_ui import MainUI
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    window = MainUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # use database to save data
    main()
