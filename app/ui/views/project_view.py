import os
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QAction
from qfluentwidgets import PushButton, FluentIcon, RoundMenu, ToolButton, MessageBox, StateToolTip

from app.core.models.project import Project, TranscribeOpt
from app.ui.components.label import AutoLabel
from app.ui.config import cfg
from app.ui.const import CONTAINER_MARGINS
from app.ui.utils import run_in_thread, clear_layout


class ProjectView(QFrame):
    sig_subtitle_list_loaded = pyqtSignal(list)
    sig_transcribe_running = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('proj-view')

        self.project: Optional[Project] = None

        self.state_tooltip = None

        self.layout = QVBoxLayout(self)
        self.layout_title = QHBoxLayout(self)
        self.layout_subtitles = QVBoxLayout(self)

        self.label_title = AutoLabel('<Loading>', self, QtCore.Qt.ElideMiddle)
        self.label_title.setObjectName('ViewTitle')
        self.btn_manage = ToolButton(FluentIcon.MORE, self)
        self.btn_manage.clicked.connect(
            lambda: self._on_btn_manage_clicked(
                self.btn_manage.mapToGlobal(QPoint()) + QPoint(self.btn_manage.width() + 5, 10)
            )
        )

        self.btn_transcribe = PushButton('开始听写', self, FluentIcon.SEND_FILL)
        self.btn_transcribe.clicked.connect(self._run_transcribe)

        self._init_signal()
        self._init_layout()

    def set_project(self, project: Project):
        self.project = project
        self.label_title.setText(self.project.name)
        self.label_title.setToolTip(self.project.name)
        self._reload_subtitle_list()

    def _init_layout(self):
        self.layout_title.addWidget(self.label_title)
        self.layout_title.addWidget(self.btn_manage)

        self.layout.addLayout(self.layout_title)
        self.layout.addLayout(self.layout_subtitles)
        self.layout.addStretch(1)
        self.layout.addWidget(self.btn_transcribe)

        self.layout.setContentsMargins(*CONTAINER_MARGINS)

    def _init_signal(self):
        self.sig_subtitle_list_loaded.connect(self._on_subtitle_list_loaded)
        self.sig_transcribe_running.connect(self._on_transcribe_running_changed)

    def _on_transcribe_running_changed(self, running: bool):
        if self.state_tooltip is None:
            self.state_tooltip = StateToolTip('正在听写中', '请耐心等待', self)
            self.state_tooltip.closeButton.hide()
        if running:
            self.btn_transcribe.setDisabled(True)
            self.state_tooltip.move(10, 10)
            self.state_tooltip.show()
        else:
            self.btn_transcribe.setDisabled(False)
            self.state_tooltip.setState(True)
            self.state_tooltip.setTitle('听写完成!')
            self.state_tooltip.setContent('')
            self.state_tooltip = None

    def _on_subtitle_list_loaded(self, filenames: list):
        clear_layout(self.layout_subtitles)

        for filename in filenames:
            layout = QHBoxLayout(self)

            label = AutoLabel(filename, self, QtCore.Qt.ElideLeft)
            label.setToolTip(filename)

            btn_translate = ToolButton(FluentIcon.EDIT, self)
            btn_translate.setToolTip('翻译')
            btn_delete = ToolButton(FluentIcon.DELETE, self)
            btn_delete.setToolTip('删除')
            btn_delete.clicked.connect(self._on_subtitle_delete_clicked(filename))

            layout.addWidget(label)
            layout.addWidget(btn_translate)
            layout.addWidget(btn_delete)
            self.layout_subtitles.addLayout(layout)

    def _reload_subtitle_list(self):
        self.sig_subtitle_list_loaded.emit(
            [
                filename
                for filename in os.listdir(self.project.path)
                if filename.endswith('.srt') or filename.endswith('.ass')
            ]
        )

    def _on_subtitle_delete_clicked(self, filename):

        def f():
            target_file = os.path.join(self.project.path, filename)
            if MessageBox('删除确认', f'真的要删除 {target_file} 吗？', self.window()).exec():
                os.remove(target_file)
                self._reload_subtitle_list()

        return f

    def _on_btn_manage_clicked(self, pos):
        menu = RoundMenu(parent=self)
        act_archive = QAction(FluentIcon.SAVE.icon(), '归档')
        act_clear_srt = QAction(FluentIcon.DELETE.icon(), '删除所有 SRT 文件')
        act_clear_ass = QAction(FluentIcon.DELETE.icon(), '删除所有 ASS 文件')
        act_delete_proj = QAction(FluentIcon.DELETE.icon(), '删除该项目')

        act_archive.triggered.connect(lambda: print(MessageBox('confirm?', 'some desc', self.window()).exec()))
        act_clear_srt.triggered.connect(lambda: print('这个功能还没做'))
        act_clear_ass.triggered.connect(lambda: print('这个功能还没做'))
        act_delete_proj.triggered.connect(self._on_act_del_proj)

        menu.addAction(act_archive)
        menu.addSeparator()
        menu.addActions([
            act_clear_srt,
            act_clear_ass,
        ])
        menu.addSeparator()
        menu.addAction(act_delete_proj)

        # show menu
        menu.exec(pos, ani=True)

    def _on_act_del_proj(self):
        if MessageBox('删除确认', '真的要删除吗？', self.window()).exec():
            self.project.delete()
            self.window().reload_projects()

    @run_in_thread
    def _run_transcribe(self, _):
        if not self.project:
            return

        opt = TranscribeOpt(
            backend=cfg.get(cfg.engine).value,
            model=cfg.get(cfg.model).value,
            quantize=cfg.get(cfg.quantize),
            lang=cfg.get(cfg.transcribe_lang).value,
            ss=0,
            t=0,
            compress_ratio_threshold=2.4,
            speedup=False,
            prompt_name='',
        )
        self.sig_transcribe_running.emit(True)
        try:
            self.project.transcribe(opt)
        except Exception as e:
            print(f'听写时发生错误: {repr(e)}')
        self.sig_transcribe_running.emit(False)
        self._reload_subtitle_list()

    # def run_translate(self):
    #     if not self.project:
    #         return
    #
    #     opt = TranscribeOpt(
    #         backend=cfg.engine,
    #         lang='ja',
    #         ss=0,
    #         t=0,
    #         compress_ratio_threshold=2.4,
    #         speedup=args.speedup,
    #         prompt_name=args.prompt,
    #     )
    #     self.project.translate(opt=opt, vocab=Data.VOCABS[args.vocab] if args.vocab else None)
