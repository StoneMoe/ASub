# coding:utf-8
import os
from enum import Enum

from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, EnumSerializer)

from app.core import Core


class Engine(Enum):
    PY_CPU = "py-cpu"
    PY_GPU = "py-gpu"
    CPP_CPU = "cpp-cpu"


class TranscribeModel(Enum):
    LARGE_V2 = "large-v2"
    MEDIUM = "medium"
    SMALL = "small"
    BASE = "base"
    TINY = "tiny"


class UILang(Enum):
    CHINESE_SIMPLIFIED = "chs"
    CHINESE_TRADITIONAL = "cht"
    ENGLISH = "en"
    AUTO = "auto"


class TranscribeLang(Enum):
    AUTO = None
    en = 'english'
    zh = 'chinese'
    de = 'german'
    es = 'spanish'
    ru = 'russian'
    ko = 'korean'
    fr = 'french'
    ja = 'japanese'
    pt = 'portuguese'
    tr = 'turkish'
    pl = 'polish'
    ca = 'catalan'
    nl = 'dutch'
    sv = 'swedish'
    it = 'italian'
    id = 'indonesian'
    hi = 'hindi'
    vi = 'vietnamese'

    @classmethod
    def options(cls):
        zh_names = {
            None: '自动检测',
            'chinese': '中文',
        }
        return [
            item.value.title() if item.value not in zh_names else zh_names[item.value]
            for item in cls
        ]


class Config(QConfig):
    """ Config of application """

    # generic
    ui_lang = OptionsConfigItem("generic", "lang",
                                UILang.AUTO,
                                OptionsValidator(UILang),
                                EnumSerializer(UILang),
                                restart=True)
    # transcribe
    engine = OptionsConfigItem("transcribe", "engine",
                               Engine.PY_CPU,
                               OptionsValidator(Engine),
                               EnumSerializer(Engine))
    model = OptionsConfigItem("transcribe", "model",
                              TranscribeModel.TINY,
                              OptionsValidator(TranscribeModel),
                              EnumSerializer(TranscribeModel))
    quantize = ConfigItem("transcribe", "quantize", False, BoolValidator())
    transcribe_lang = OptionsConfigItem("transcribe", "lang",
                                        TranscribeLang.AUTO,
                                        OptionsValidator(TranscribeLang),
                                        EnumSerializer(TranscribeLang))


cfg = Config()
qconfig.load(os.path.join(Core.BASE_DIR, 'config.json'), cfg)
