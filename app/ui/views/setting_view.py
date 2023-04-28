from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, setTheme, isDarkTheme)

from app.core import Core
from app.core.utils.env import check_ffmpeg
from app.ui.config import cfg, TranscribeLang
from app.ui.const import APP_VER
from app.ui.utils import res_dir


class SettingView(ScrollArea):
    aboutSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('setting-view')

        self.scroll_area = QWidget()
        self.layout = ExpandLayout(self.scroll_area)

        # setting label
        self.label_setting = QLabel('设置', self)

        # general
        self.group_general = SettingCardGroup('通用', self.scroll_area)
        self.card_theme = ComboBoxSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            '主题',
            '设置应用的主题',
            texts=['明亮', '暗黑', '跟随系统设置'],
            parent=self.group_general
        )
        self.card_ui_lang = ComboBoxSettingCard(
            cfg.ui_lang,
            FIF.LANGUAGE, '语言',
            '设置界面语言',
            texts=['简体中文', '繁體中文', 'English', '跟随系统设置'],
            parent=self.group_general
        )

        # transcribe
        self.group_transcribe = SettingCardGroup('听写', self.scroll_area)
        self.card_engine = ComboBoxSettingCard(
            cfg.engine,
            FIF.CODE, '引擎',
            '设置想使用的计算模式',
            texts=['CPU', 'CUDA', 'GGML-CPU'],
            parent=self.group_transcribe
        )
        self.card_model = ComboBoxSettingCard(
            cfg.model,
            FIF.MENU, '模型',
            '设置想使用的听写模型，模型越大，速度越慢，准确度越高',
            texts=['大 (~8 GB)', '中 (~5 GB)', '小 (~2 GB)', '基本 (~1 GB)', '迷你 (~1 GB)'],
            parent=self.group_transcribe
        )
        self.card_quantize = SwitchSettingCard(
            FIF.UPDATE,
            '模型量化',
            '量化到 int8 以尝试减少系统资源的使用，可能影响准确度',
            configItem=cfg.quantize,
            parent=self.group_transcribe
        )
        self.card_transcribe_lang = ComboBoxSettingCard(
            cfg.transcribe_lang,
            FIF.LANGUAGE, '输出语言',
            '以第一个时间窗口为基准自动检测，或手动选择输出语言',
            texts=TranscribeLang.options(),
            parent=self.group_transcribe
        )

        # about
        self.group_about = SettingCardGroup('关于', self.scroll_area)
        self.card_diagnose = PrimaryPushSettingCard(
            '诊断',
            FIF.HELP, '运行诊断',
            '对当前系统环境进行诊断',
            self.group_about
        )
        self.card_feedback = PrimaryPushSettingCard(
            '反馈',
            FIF.FEEDBACK, '提供反馈',
            '帮助我们改善这个应用',
            self.group_about
        )
        self.card_about = PrimaryPushSettingCard(
            '检查更新',
            FIF.INFO, self.tr('关于'),
            f'© 版权所有 2023, StoneMoe. 版本 {APP_VER}',
            self.group_about
        )

        self._init_widget()

    def _init_widget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scroll_area)
        self.setWidgetResizable(True)

        # initialize style sheet
        self._set_qss()

        # initialize layout
        self._init_layout()
        self._connect_signals()

    def _init_layout(self):
        self.label_setting.move(32, 64)

        # add cards to group
        self.group_general.addSettingCard(self.card_theme)
        self.group_general.addSettingCard(self.card_ui_lang)

        self.group_transcribe.addSettingCard(self.card_engine)
        self.group_transcribe.addSettingCard(self.card_model)
        self.group_transcribe.addSettingCard(self.card_quantize)
        self.group_transcribe.addSettingCard(self.card_transcribe_lang)

        self.group_about.addSettingCard(self.card_diagnose)
        self.group_about.addSettingCard(self.card_feedback)
        self.group_about.addSettingCard(self.card_about)

        # add card group to layout
        self.layout.setContentsMargins(32, 10, 32, 0)
        self.layout.addWidget(self.group_general)
        self.layout.addWidget(self.group_transcribe)
        self.layout.addWidget(self.group_about)

    def _set_qss(self):
        """set style sheet"""
        self.scroll_area.setObjectName('scrollWidget')
        self.label_setting.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(res_dir(f'app/ui/resource/qss/{theme}/setting_view.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _show_restart_tooltip(self):
        """show restart tooltip"""
        InfoBar.warning(
            'a', 'b',
            parent=self.window()
        )

    def _on_btn_diagnose_click(self):
        m = MessageBox(
            '扫描结果',
            f'运行位置: {Core.EXEC_DIR}\n'
            # f'CUDA: {check_cuda().human_read()}\n'
            f'FFmpeg: {check_ffmpeg().human_read()}\n',
            self.window()
        )
        m.exec()

    def _on_theme_change(self, theme: Theme):
        """ theme changed slot """
        setTheme(theme)
        self._set_qss()

    def _connect_signals(self):
        """connect signal to slot"""
        cfg.appRestartSig.connect(self._show_restart_tooltip)
        cfg.themeChanged.connect(self._on_theme_change)

        # about
        self.card_about.clicked.connect(self.aboutSig)
        self.card_diagnose.clicked.connect(self._on_btn_diagnose_click)
        self.card_feedback.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('http://example.com')))
