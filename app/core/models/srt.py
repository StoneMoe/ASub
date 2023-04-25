import dataclasses
import os
from datetime import timedelta
from pprint import pprint
from typing import List

from app.core.utils.translate import youdao_translate


def format_srt_time(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    seconds, milliseconds = divmod(seconds, 1)
    milliseconds = int(milliseconds * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    srt_time = "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
    return srt_time


@dataclasses.dataclass
class SRTEntry:
    index: str
    time: str
    text: str

    @classmethod
    def load(cls, text: str):
        p1, p2, p3, *_ = text.split('\n')
        return SRTEntry(p1, p2, p3)

    def dumps(self):
        """dump to standard SRT entry format"""
        return f'{self.index}\n{self.time}\n{self.text}'


class SRTFile:
    filepath: str
    entries: List[SRTEntry]

    def __init__(self, source: str | list):
        self.filepath = ''
        self.entries = []

        match source:
            case str():
                self.load_from_file(filepath=source)
            case list():
                self.load_from_segments(segments=source)
            case _:
                pprint(source)
                raise NotImplementedError

    def load_from_segments(self, segments: List[dict]):
        for segment in segments:
            start_time = format_srt_time(timedelta(seconds=segment['start']))
            end_time = format_srt_time(timedelta(seconds=segment['end']))
            text: str = segment['text']
            segment_id = segment['id'] + 1
            srt_item = f"{segment_id}\n" \
                       f"{start_time} --> {end_time}\n" \
                       f"{text.lstrip()}"
            self.entries.append(SRTEntry.load(srt_item))

    def load_from_file(self, filepath: str):
        with open(filepath, encoding='utf8') as f:
            file_content = f.read()
            self.filepath = filepath
            self.entries = [SRTEntry.load(item) for item in file_content.split('\n\n') if item]
            print(f'自 {filepath} 载入了 {len(self.entries)} 个条目')

    def dump(self, filepath: str = None):
        if filepath:
            self.filepath = filepath
        if not self.filepath:
            raise ValueError('未设置 SRT 文件的写入路径')
        with open(self.filepath, 'w', encoding='utf-8') as f:
            for entry in self.entries:
                f.write(entry.dumps() + '\n\n')
        print(f'SRT 文件已保存至 {self.filepath}')

    def translate(self, vocab=None):
        """translate and write to new file in realtime"""
        target_file = f"{self.filepath}.translated.{vocab or '_'}.srt"
        if os.path.isfile(target_file):
            print(f'文件 "{target_file}" 已存在，跳过翻译')
            return
        if vocab:
            print(f'正在使用术语表 {vocab}')

        source_text = '\n'.join([item.text for item in self.entries])
        translated_text = youdao_translate(source_text, vocab_id=vocab)
        lines = translated_text.split('\n')
        if len(self.entries) != len(lines):
            print(f'原 {len(self.entries)} 条，翻译后 {len(lines)} 条。无法应用翻译结果')
            return

        with open(target_file, mode='w+', encoding='utf8') as f:
            for i, line in enumerate(lines):
                f.write(self.entries[i].dumps())
                f.write('\n')
                f.write(line)
                f.write('\n\n')
