import os
from typing import Optional


def test_files(*file_paths: str) -> Optional[str]:
    """check filepaths in order, return if exist"""
    for path in file_paths:
        if os.path.isfile(path):
            return path
    return None
