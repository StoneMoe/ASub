import os

from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog
from qfluentwidgets import PushButton

from app.core.models.project import Project
from app.ui.const import CONTAINER_MARGINS
from app.core import Consts


class HomeView(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('home-view')

        self.layout = QVBoxLayout(self)

        self.title = QLabel(Consts.APP_NAME)
        self.title.setObjectName('app-title')
        self.desc = QLabel('在下方新建项目，或在左侧查看已有项目')
        self.desc.setObjectName('app-desc')

        self.sub_layout = QHBoxLayout(self)
        self.left = QVBoxLayout(self)
        self.right = QVBoxLayout(self)

        self.left_title = QLabel('创建新项目', self)
        self.left_btn = PushButton('选择文件', self)
        self.left_btn.clicked.connect(self.create_proj_from_file)

        self.right_title = QLabel('批量导入', self)
        self.right_btn = PushButton('选择目录', self)
        self.right_btn.clicked.connect(lambda: print('这个功能还没做'))

        self.init_layout()

    def init_layout(self):
        self.layout.setContentsMargins(*CONTAINER_MARGINS)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.desc)
        self.layout.addLayout(self.sub_layout)

        self.sub_layout.addLayout(self.left, 1)
        self.sub_layout.addLayout(self.right, 1)

        self.left.addStretch(1)
        self.left.addWidget(self.left_title)
        self.left.addWidget(self.left_btn)
        self.left.addStretch(1)

        self.right.addStretch(1)
        self.right.addWidget(self.right_title)
        self.right.addWidget(self.right_btn)
        self.right.addStretch(1)

    def create_proj_from_file(self):
        fullpath, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "MP4 (*.mp4);;MP3 (*.mp3)")
        if not fullpath:
            return

        filename = os.path.basename(fullpath)
        proj_name = os.path.splitext(filename)[0]
        Project.bulk_create([(proj_name, fullpath)])
        self.window().reload_projects()

    def batch_from_folder(self):
        pass
