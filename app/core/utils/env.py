import os
import subprocess
import sys
from enum import Enum

from app.core.utils.generic import info


class CUDAStatus(Enum):
    READY = 0
    NOT_INSTALLED = 1
    VER_MISMATCH = 2

    def human_read(self):
        return {
            CUDAStatus.READY: '正常',
            CUDAStatus.NOT_INSTALLED: '未安装',
            CUDAStatus.VER_MISMATCH: '版本不正确',
        }[self]


class FFMpegStatus(Enum):
    READY = 0
    NOT_INSTALLED = 1
    UNKNOWN_ERR = 255

    def human_read(self):
        return {
            FFMpegStatus.READY: '正常',
            FFMpegStatus.NOT_INSTALLED: '未安装',
        }[self]


def check_cuda():
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0 and "cuda_11.7" in result.stdout:
            return CUDAStatus.READY
        else:
            return CUDAStatus.VER_MISMATCH
    except FileNotFoundError:
        return CUDAStatus.NOT_INSTALLED


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return FFMpegStatus.READY
    except FileNotFoundError:
        return FFMpegStatus.NOT_INSTALLED
    except Exception:
        return FFMpegStatus.UNKNOWN_ERR


def install_ffmpeg():
    """Powered by ChatGPT, windows only"""
    winget_check_command = "where winget"
    result = subprocess.run(winget_check_command, shell=True, stdout=subprocess.PIPE)
    if result.returncode != 0:
        info("您的系统上没有 winget，无法自动安装 FFmpeg")
        return

    package_name = "ffmpeg"
    winget_install_command = f"winget install {package_name}"
    result = subprocess.run(winget_install_command, shell=True)
    if result.returncode == 0:
        info("FFmpeg 安装成功")
    else:
        info("安装 FFmpeg 失败")


def get_document_folder():
    """Powered by ChatGPT"""
    if os.name == 'nt':  # If it's Windows
        # Try to get the document folder path from the registry
        try:
            import winreg
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders")
            document_folder_path = winreg.QueryValueEx(reg_key, "Personal")[0]
            winreg.CloseKey(reg_key)
            return os.path.expandvars(document_folder_path)
        except:
            pass

        # Try to get the document folder path from the environment variables
        try:
            document_folder_path = os.environ["USERPROFILE"] + "\\Documents"
            if os.path.isdir(document_folder_path):
                return document_folder_path
        except:
            pass

        # Try to get the document folder path from the known folder GUID
        try:
            from ctypes import windll, create_unicode_buffer

            # Define the GUID for the Documents folder
            documents_guid = '{FDD39AD0-238F-46AF-ADB4-6C85480369C7}'

            # Call the SHGetKnownFolderPath function to get the folder path
            buf = create_unicode_buffer(1024)
            if windll.shell32.SHGetKnownFolderPath(documents_guid, 0, None, buf) == 0:
                document_folder_path = buf.value
                if os.path.isdir(document_folder_path):
                    return document_folder_path
        except:
            pass

    # If all else fails, return the default document folder path
    return os.path.expanduser("~/Documents")


def res_dir(relative_path):
    """Get application resource file"""
    try:
        # noinspection PyUnresolvedReferences,PyProtectedMember
        base_path = sys._MEIPASS  # PyInstaller one file mode
    except AttributeError:
        base_path = get_exec_dir()

    return os.path.join(base_path, relative_path)


def get_base_dir():
    return os.path.join(get_document_folder(), 'ASub')


def get_exec_dir():
    return os.path.dirname(os.path.abspath(sys.argv[0]))
