import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app.core import Core
from app.ui.main_window import MainWindow


def launch():
    if Core.DPI_SCALE:
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = '1'  # [1, 1.25, 1.5, 1.75, 2]

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    w = MainWindow()
    w.show()
    app.exec()
