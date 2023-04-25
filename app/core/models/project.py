import dataclasses
import os
import shutil
import subprocess
from typing import List, Optional

from app.core import Core
from app.core.consts import Consts
from app.core.models.srt import SRTFile
from app.core.utils.generic import test_files
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
        self.path = f'{Core.DIR_PROJECTS}/{name}'
        try:
            os.makedirs(self.path)
            print(f'已创建目录 {self.path}')
        except OSError as e:  # directory existed
            if existed_err:
                raise e

    def _prepare(self):
        print(f'正在预处理 "{self.path}" 的音频')
        wav_path = f'{self.path}/source.wav'
        target_wav = test_files(wav_path)
        target_mp4 = test_files(f'{self.path}/source.mp4', f'{self.path}/{self.name}.mp4',
                                f'{self.path}/{self.name}.mp3')
        if target_wav:
            print(f'找到了 "{target_wav}"，不再预处理')
        elif target_mp4:
            print(f'找到了 "{target_mp4}"，开始预处理')
            cmd = f'ffmpeg -i "{target_mp4}" -vn -ac 1 -ar 16000 -c:a pcm_s16le "{wav_path}"'
            print(f'正在运行 {cmd}')
            proc = subprocess.Popen(cmd, shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in proc.stdout:
                print(line.decode(Core.CODEC).rstrip())
            return_code = proc.wait()
            print('预处理失败' if return_code != 0 else '预处理成功')
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
            print(f'文件 "{target_file}" 已存在，跳过听写')
            return target_file

        print(f'使用 {opt}')
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
                print('正在加载模型')
                import whisper
                import torch
                model = whisper.load_model(opt.model, download_root='data/whisper_model', device='cpu')
                if opt.quantize:
                    print('正在量化模型')
                    model = torch.quantization.quantize_dynamic(
                        model, {torch.nn.Linear}, dtype=torch.qint8
                    )
                if opt.backend == 'py-gpu':
                    print('正在加载至显卡')
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

        print('听写完成')

    def translate(self, opt: TranscribeOpt, vocab=None):
        srt = SRTFile(source=opt.make_srt_filepath(self.name, self.path))
        srt.translate(vocab=vocab)

    @classmethod
    def list(cls) -> List[str]:
        """list all projects"""
        names = os.listdir(Core.DIR_PROJECTS)
        directories = [name for name in names if os.path.isdir(os.path.join(Core.DIR_PROJECTS, name))]
        directories = sort_titles(directories)
        return directories

    @classmethod
    def bulk_create(cls, targets: List[tuple]):
        print(f'正在创建 {len(targets)} 个工程')
        for proj_name, filepath in targets:
            try:
                proj = Project(proj_name, existed_err=True)
            except OSError:
                print(f'"{proj_name}" 已存在，不再创建')
                continue

            if filepath:
                dst_filepath = os.path.join(proj.path, os.path.basename(filepath))
                print(f'正在将 {filepath} 复制到 {dst_filepath}')
                shutil.copy(filepath, dst_filepath)
                print('复制完毕')