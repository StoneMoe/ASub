from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QTableWidgetItem, QDialog
from qfluentwidgets import TableWidget, isDarkTheme
from qframelesswindow import FramelessWindow

from app.core.models.srt import SRTFile
from app.ui.const import CONTAINER_MARGINS
from app.ui.utils import res_dir


class SubtitleWindow(QDialog, FramelessWindow):
    def __init__(self, filepath: str, parent=None):
        super().__init__(parent)
        self.srt_file = SRTFile(filepath)
        self.hBoxLayout = QVBoxLayout(self)
        self.tableView = TableWidget(self)
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self._save_subtitle_file)

        self.hBoxLayout.setContentsMargins(*CONTAINER_MARGINS)
        self.hBoxLayout.addWidget(self.tableView)
        self.hBoxLayout.addWidget(self.saveButton)

        self.init_window()
        self._load_subtitle_file()

    def _load_subtitle_file(self):
        self.tableView.setWordWrap(False)
        self.tableView.setRowCount(len(self.srt_file.entries))
        self.tableView.setColumnCount(3)
        for i, entry in enumerate(self.srt_file.entries):
            self.tableView.setItem(i, 0, QTableWidgetItem(entry.index))
            self.tableView.setItem(i, 1, QTableWidgetItem(entry.time))
            self.tableView.setItem(i, 2, QTableWidgetItem(entry.text))

        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['Index', 'Time', 'Text'])
        self.tableView.resizeColumnsToContents()

    def _save_subtitle_file(self):
        for i in range(self.tableView.rowCount()):
            self.srt_file.entries[i].index = self.tableView.item(i, 0).text()
            self.srt_file.entries[i].time = self.tableView.item(i, 1).text()
            self.srt_file.entries[i].text = self.tableView.item(i, 2).text()

        self.srt_file.dump()

    def init_window(self):
        self.setWindowTitle(f'编辑 {self.srt_file.filepath}')
        self.resize(625, 700)
        self._set_qss()

    def _set_qss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(res_dir(f'app/ui/resource/qss/{color}/style.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())
