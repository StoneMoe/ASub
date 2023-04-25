from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.ui.const import NO_MARGINS


class StubWidget(QFrame):

    def __init__(self, parent, objname: str, text: str, desc: str = ''):
        super().__init__(parent=parent)
        self.setObjectName(objname)

        self.title = QLabel(text, self)
        self.title.setObjectName("title")
        self.desc = QLabel(desc, self)
        self.desc.setObjectName("desc")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.title, 1)
        self.layout.addWidget(self.desc, 1)

        # leave some space for title bar
        self.layout.setContentsMargins(*NO_MARGINS)
