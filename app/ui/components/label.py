from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class AutoLabel(QLabel):
    def __init__(self, text, parent=None, elide_mode=None):
        super().__init__(text, parent)
        self._raw_text = text
        self._elide_mode = elide_mode if elide_mode is not None else Qt.ElideMiddle
        self._eliding = False

    def _get_elided_text(self):
        return self.fontMetrics().elidedText(self._raw_text, self._elide_mode, self.width())

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        if self._eliding:
            return

        self._eliding = True
        super().setText(self._get_elided_text())
        self._eliding = False

    def setText(self, text):
        self._raw_text = text
        super().setText(self._get_elided_text())
