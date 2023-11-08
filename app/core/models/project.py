import dataclasses
import os
import shutil
from subprocess import Popen
from typing import List, Optional

import ffmpeg

from app.core import Core, Consts
from app.core.models.srt import SRTFile
from app.core.utils.env import check_ffmpeg, FFMpegStatus
from app.core.utils.generic import test_files, info
from app.core.utils.sort import sort_titles


@dataclasses.dataclass
class TranscribeOpt:
    """
    :param backend: whisper implementation
    :param model: whisper model name
    :param quantize: whisper model quantization switch
    :param ss: transcribe start second
    :param t: transcribe time duration(second)
    :param compress_ratio_threshold: 2.4 ~ 3 is recommended, segments higher than this will be re-inferenced
    :param speedup: double speed, decrease quality
    :param prompt_name: name
    """
    backend: str
    model: str
    quantize: bool
    lang: Optional[str]
    ss: int  # TODO: implement in whisper.py mode
    t: int  # TODO: implement in whisper.py mode
    compress_ratio_threshold: float
    speedup: bool  # TODO: implement in whisper.py mode
    prompt_name: str

    def make_srt_filepath(self, name: str, path: str) -> str:
        return f'{path}/' \
               f'{name}' \
               f'[{self.backend}]' \
               f'[{self.model}]' \
               f'[q{int(self.quantize)}]' \
               f'[L{self.lang or "auto"}]' \
               f'[t{"FULL" if not (self.ss and self.t) else f"{self.ss}-{self.ss + self.t}"}]' \
               f'[e{self.compress_ratio_threshold}]' \
               f'[s{int(self.speedup)}]' \
               f'[p{self.prompt_name or "-"}]' \
               f'.srt'


class Project:
    path: str  # 工程目录（相对位置）
    name: str  # 工程名称

    def __init__(self, name: str, existed_err=False):
        self.name = name
        self.path = os.path.join(Core.PROJ_DIR, name)
        try:
            os.makedirs(self.path)
            info(f'已创建目录 {self.path}')
        except OSError as e:  # directory existed
            if existed_err:
                raise e

    def _prepare(self):
        info(f'正在预处理 "{self.name}" 的音频')
        tmp_path = os.path.join(self.path, 'source.wav')
        tmp_file = test_files(tmp_path)
        src_file = test_files(
            os.path.join(self.path, 'source.mp4'),
            os.path.join(self.path, f'{self.name}.mp4'),
            os.path.join(self.path, f'{self.name}.mp3')
        )
        if tmp_file:
            info(f'找到了临时文件 "{tmp_file}"，跳过预处理')
        elif src_file:
            info(f'找到了 "{src_file}"，开始预处理')
            if check_ffmpeg() != FFMpegStatus.READY:
                raise EnvironmentError('FFMpeg尚未安装')
            proc: Popen[bytes] = ffmpeg.input(src_file) \
                .output(tmp_path, format='wav', acodec='pcm_s16le', ac=1, ar=16000) \
                .overwrite_output() \
                .run_async(pipe_stdout=True, pipe_stderr=True)
            out, err = proc.communicate()
            return_code = proc.wait()
            if return_code != 0:
                raise ChildProcessError('无法提取音频')
            info('预处理成功')
        else:
            raise FileNotFoundError(f'请将同名 mp4 文件放置在 {self.path}')

    def delete(self):
        """Delete project folder"""
        shutil.rmtree(self.path)

    def transcribe(self, opt: TranscribeOpt):
        """
        transcribe wav audio to SRT

        :return: transcribe result file path
        """
        self._prepare()

        target_file = opt.make_srt_filepath(name=self.name, path=self.path)
        if os.path.isfile(target_file):
            info(f'文件 "{target_file}" 已存在，跳过听写')
            return target_file

        info(f'使用 {opt}')
        match opt.backend:
            # case Engine.CPP_CPU:
            #     ext = ''
            #     if opt.compress_ratio_threshold:
            #         ext += f' -et {opt.compress_ratio_threshold} '
            #     if opt.prompt_name:
            #         ext += f' --prompt "{DB.PROMPTS[opt.prompt_name]}" '
            #     if opt.speedup:
            #         ext += f' -su '
            #     if opt.ss and opt.t:
            #         ss = opt.ss * 1000
            #         t = opt.t * 1000
            #         if opt.speedup:
            #             ss /= 2
            #             t /= 2
            #         ext += f' -ot {ss} -d {t} '
            #     cmd = f".\\whisper\\main.exe -m data/whisper_model/ggml-large-v2.bin " \
            #           f"-pp -osrt -l {opt.lang} -t 8 {ext} -f {self.path}/source.wav -of {target_file.rstrip('.srt')}"
            #     print(f'运行: {cmd}')
            #     proc = subprocess.Popen(cmd, shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE)
            #     for line in proc.stdout:
            #         print(line.decode(Core.CODEC).rstrip())
            case 'py-gpu' | 'py-cpu':
                info('正在加载模型')
                import whisper
                import torch
                model = whisper.load_model(opt.model, download_root='whisper_model', device='cpu')
                if opt.quantize:
                    info('正在量化模型')
                    model = torch.quantization.quantize_dynamic(
                        model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                if opt.backend == 'py-gpu':
                    info('正在加载至显卡')
                    model.to('cuda')
                result = model.transcribe(
                    audio=f'{self.path}/source.wav',
                    language=opt.lang,
                    compression_ratio_threshold=opt.compress_ratio_threshold,
                    initial_prompt=Consts.PROMPTS[opt.prompt_name],
                    verbose=True,
                )

                del model
                torch.cuda.empty_cache()

                segments = result['segments']
                srt = SRTFile(source=segments)
                srt.dump(target_file)
            case _:
                raise NotImplementedError(f'{opt.backend} 引擎尚未支持')

        info('听写完成')

    def translate(self, opt: TranscribeOpt, vocab=None):
        srt = SRTFile(source=opt.make_srt_filepath(self.name, self.path))
        srt.translate(vocab=vocab)

    @classmethod
    def list(cls) -> List[str]:
        """list all projects"""
        names = os.listdir(Core.PROJ_DIR)
        directories = [name for name in names if os.path.isdir(os.path.join(Core.PROJ_DIR, name))]
        directories = sort_titles(directories)
        return directories

    @classmethod
    def bulk_create(cls, targets: List[tuple]):
        info(f'正在创建 {len(targets)} 个工程')
        for proj_name, filepath in targets:
            try:
                proj = Project(proj_name, existed_err=True)
            except OSError:
                info(f'"{proj_name}" 已存在，不再创建')
                continue

            if filepath:
                dst_filepath = os.path.join(proj.path, os.path.basename(filepath))
                info(f'正在将 {filepath} 复制到 {dst_filepath}')
                shutil.copy(filepath, dst_filepath)
                info('复制完毕')
