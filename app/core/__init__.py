import os
import sys

from app.core.utils.env import get_document_folder


class Core:
    BASE_DIR = os.path.join(get_document_folder(), 'ASub')
    PROJ_DIR = os.path.join(BASE_DIR, 'projects')
    EXEC_DIR: str = os.path.dirname(os.path.abspath(sys.argv[0]))
    CODEC: str = 'utf-8'
    DPI_SCALE = True

    @classmethod
    def init(cls):
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        os.makedirs(cls.PROJ_DIR, exist_ok=True)
        os.chdir(Core.BASE_DIR)
