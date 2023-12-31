import functools
import os
import subprocess
import sys
import threading

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit

from app.core import Core


class StdoutProxy(QObject):
    write_signal = pyqtSignal(str)

    def __init__(self, text_edit_widget: QTextEdit):
        super().__init__()
        self.target = text_edit_widget
        self.write_signal.connect(self._on_sig)

    def _on_sig(self, data: str):
        self.target.moveCursor(QTextCursor.MoveOperation.End)
        self.target.insertPlainText(data)
        self.target.moveCursor(QTextCursor.MoveOperation.End)

    def write(self, text):
        self.write_signal.emit(text)

    def flush(self):  # Stub
        pass


def run_in_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args and kwargs:
            t = threading.Thread(target=func, args=args, kwargs=kwargs)
        elif args:
            t = threading.Thread(target=func, args=args)
        else:
            t = threading.Thread(target=func)
        t.daemon = True
        t.start()
        return t

    return wrapper


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())


def open_folder(folder_path):
    """Open specific folder in file explorer application"""
    if os.name == 'nt':  # Windows
        os.startfile(folder_path)
    elif os.name == 'posix':  # Linux, macOS, etc.
        subprocess.Popen(['xdg-open', folder_path])
    else:
        raise OSError(f'Unsupported platform: {os.name}')
