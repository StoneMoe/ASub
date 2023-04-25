import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QApplication, QVBoxLayout
from qfluentwidgets import setTheme, Theme, NavigationInterface, FluentIcon, NavigationItemPosition, isDarkTheme, \
    TextEdit
from qframelesswindow import FramelessWindow

from app.core.models.project import Project
from app.ui.config import cfg
from app.ui.const import APP_NAME
from app.ui.utils import StdoutProxy
from app.ui.views import HomeView, ProjectView, SettingView
from app.ui.widgets import FancyTitleBar


class MainWindow(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.hide()
        self.container = QHBoxLayout(self)

        self.nav = NavigationInterface(self)
        self.main = QVBoxLayout(self)

        self.stack = QStackedWidget(self)
        self.log_area = TextEdit(self)
        self.log_area.setReadOnly(True)

        # stack views
        self.home_view = HomeView(self)
        self.project_view = ProjectView(self)
        self.setting_view = SettingView(self)

        # attach everything
        self._init_signals()
        self._init_window()
        self._init_layout()

        self.reload_projects()

        self.show()

    def _init_signals(self):
        sys.stdout = StdoutProxy(text_edit_widget=self.log_area)
        sys.stderr = StdoutProxy(text_edit_widget=self.log_area)
        cfg.themeChanged.connect(self._on_theme_change)
        cfg.themeChanged.emit(cfg.get(cfg.themeMode))

    def _init_window(self):
        self.setMinimumSize(700, 500)
        self.resize(1024, 700)

        self.setTitleBar(FancyTitleBar(self))
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        self.setWindowIcon(QIcon('app/ui/resource/logo.jpg'))
        self.setWindowTitle(APP_NAME)

        # screen center
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _init_layout(self):
        self.container.setSpacing(0)
        self.container.setContentsMargins(0, 0, 0, 0)

        self.container.addWidget(self.nav)
        self.container.addLayout(self.main)

        # nav
        self.nav.addItem(
            routeKey=self.home_view.objectName(),
            icon=FluentIcon.HOME, text='主页',
            onClick=lambda: self._switch_to(self.home_view)
        )
        self.nav.setCurrentItem(self.home_view.objectName())
        self.nav.addItem(
            routeKey=self.setting_view.objectName(),
            icon=FluentIcon.SETTING,
            text='设置',
            onClick=lambda: self._switch_to(self.setting_view),
        )
        self.nav.addSeparator()

        # main
        self.main.addWidget(self.stack)
        self.main.addWidget(self.log_area)
        self.main.setStretchFactor(self.stack, 5)
        self.main.setStretchFactor(self.log_area, 1)

        # main - stack
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.project_view)
        self.stack.addWidget(self.setting_view)
        self.stack.currentChanged.connect(self._on_view_changed)

        self.titleBar.raise_()
        self.nav.displayModeChanged.connect(self.titleBar.raise_)
        self.nav.panel.expand()

    def _on_theme_change(self, theme: Theme):
        setTheme(theme)
        self._set_qss()

    def _on_view_changed(self, index):
        widget = self.stack.widget(index)
        self.nav.setCurrentItem(widget.objectName())

    def _set_qss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'app/ui/resource/qss/{color}/style.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _switch_to(self, widget):
        self.stack.setCurrentWidget(widget)

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())

    def reload_projects(self):
        self._switch_to(self.home_view)

        for route_key in list(self.nav.panel.items.keys()):
            if route_key.startswith('nav-proj-item'):
                self.nav.removeWidget(route_key)

        def switch_to_proj(_proj_name: str):
            def f():
                self.project_view.set_project(Project(_proj_name))
                self._switch_to(self.project_view)

            return f

        for i, name in enumerate(Project.list()):
            self.nav.addItem(
                f'nav-proj-item{i}',
                FluentIcon.FOLDER, name,
                switch_to_proj(name),
                position=NavigationItemPosition.SCROLL
            )
