import os
import sys


class Core:
    DIR_PROJECTS = './data/projects'
    CODEC: str = 'utf-8'
    EXEC_PATH: str = os.path.dirname(os.path.abspath(sys.argv[0]))
    DPI_SCALE = True

    @classmethod
    def init(cls):
        os.chdir(Core.EXEC_PATH)
        os.makedirs(cls.DIR_PROJECTS, exist_ok=True)
