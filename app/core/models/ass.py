import dataclasses
import os
from typing import Dict, Any, Tuple
from typing import List

from app.core.utils.generic import info


@dataclasses.dataclass
class ASSEntry:
    layer: str
    start_time: str
    end_time: str
    style: str
    name: str
    margin_l: str
    margin_r: str
    margin_v: str
    effect: str
    text: str

    @classmethod
    def load(cls, text: str):
        p0, p1, p2, p3, p4, p5, p6, p7, p8, p9 = text.split(',', maxsplit=9)
        return ASSEntry(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9)

    def dumps(self):
        """dump to standard ASS entry format"""
        return f'{self.layer},{self.start_time},{self.end_time},{self.style},{self.name},{self.margin_l},{self.margin_r},{self.margin_v},{self.effect},{self.text}'


class ASSFile:
    filepath: str
    entries: Dict[str, List[Tuple[str, Any]]]  # {SectionName: [(Key: Value)]}

    def __init__(self, filepath: str):
        with open(filepath, encoding='utf-8-sig') as f:  # Aegisub use UTF-8 with little-endian (\ufeff)
            file_content = f.read()

        self.filepath = filepath
        self.entries = {}

        cursor = ''  # current section
        for line in file_content.splitlines():
            line = line.strip()

            if not line or line.startswith(';'):  # Comment & empty line
                continue
            if line.startswith('[') and line.endswith(']'):  # [Section]
                cursor = line.strip('[]')
                self.entries[cursor] = []
                continue
            if cursor:  # Key: Value
                name, data = line.split(':', maxsplit=1)
                self.entries[cursor].append((name.strip(), data.strip()))
                continue
        info(f'自 {filepath} 载入了 {len(self.entries)} 个数据块')

    def translate(self, vocab=None):
        """translate and write to new file in realtime"""
        target_file = f"{self.filepath}.translated.{vocab or '_'}.ass"
        if os.path.isfile(target_file):
            info(f'文件 "{target_file}" 已存在，跳过翻译')
            return
        if vocab:
            info(f'正在使用术语表 {vocab}')

        # TODO: ASS subtitle file translate support


if __name__ == '__main__':
    test_data = """Dialogue: 0,0:00:14.32,0:00:17.48,安济知佳,,0,0,0,,嚓嚓 嚓嚓嚓嚓\\N{\\r安済知佳}ちゃちゃちゃちゃちゃちゃ
Dialogue: 0,0:00:17.84,0:00:21.08,安济知佳,,0,0,0,,\\N{\\r安済知佳}Happy birthday to you
Dialogue: 0,0:00:21.53,0:00:24.59,安济知佳,(该样式的此行与下一行之间的间隔小于300毫秒，请调整),0,0,0,,multi,part,seperate,by,comma
Dialogue: 0,0:00:21.53,0:00:24.59,安济知佳,(该样式的此行与下一行之间的间隔小于300毫秒，请调整),0,0,0,,\\N{\\r安済知佳}Happy birthday to you"""
    for test_line in test_data.split('\n'):
        o = ASSEntry.load(test_line)
        print('OK' if o.dumps() == test_line else 'NotEqual', '-', o)
