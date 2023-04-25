import sys

from PyQt5.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def launch():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
