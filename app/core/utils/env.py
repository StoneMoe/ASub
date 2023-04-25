import subprocess
from enum import Enum


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
