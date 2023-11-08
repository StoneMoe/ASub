import os

from app.core.utils.env import get_exec_dir, get_base_dir, res_dir


class Core:
    EXEC_DIR: str = get_exec_dir()
    BASE_DIR: str = get_base_dir()
    PROJ_DIR: str = os.path.join(BASE_DIR, 'projects')
    CODEC: str = 'utf-8'
    DPI_SCALE: bool = True

    @classmethod
    def init(cls):
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        os.makedirs(cls.PROJ_DIR, exist_ok=True)
        os.chdir(Core.BASE_DIR)


class Consts:
    APP_NAME = 'ASub'
    APP_VER = open(res_dir('VERSION'), mode='r', encoding=Core.CODEC).read().strip()
    VOCABS = {
        'LYCO': 'CD62BF332309446A980443F75F9B8FE4'
    }
    PROMPTS = {
        None: None,
        '': None,
        'LYCOFULL': 'サブキャラクターデザイン 春川フキ いのうえたきな 音響監督 あんざいちか 河瀬茉希 ALIVE '
                    'くのみさき うえだようじ リコリス ストーリー原案 松岡禎丞 吉田光平 こしみずあみ リコリコ '
                    'すずきごう 美術監督 A-1Pictures 色彩設計 声優 佐々木梓 若山詩音 まつおかよしつぐ おとめサクラ '
                    '睦月周平 リコラジ リコリコラジオ 榊孝辅 鈴木豪 安済知佳 そうみようこ アサウラ 六七質 小市眞琴 '
                    'ウォールナット キャラクターデザイン 井ノ上たきな 美術設定 乙女サクラ にしきぎちさと 中原ミズキ '
                    '足立慎吾 岡本穂高 ClariS こいちまこと 丸山裕介 久野美咲 総作画監督 リコリス・リコイル 須藤瞳 '
                    'プロップデザイン 榊原優希 沢田犬二 青嶋俊明 さわだけんじ 安済 CGディレクター 原作 まじま 撮影監督 '
                    '吉松シンジ 銃器・アクション監修 池田真依子 森岡俊宇 ミカ アイキャッチ わかやましおん あだちしんご '
                    'SpiderLily くすのき 真島 小清水亜美 まゆやまゆすけ さユり 楠木 ロボ太 副監督 はるかわフキ やまもとゆみこ '
                    '錦木千束 編集 さかきはらゆうき シーン いみぎむる 竹内由香里 上田燿司 すどうひとみ さかきこうすけ '
                    '山本由美子 朱原デーナ 晶貴孝二 詩音ちゃん からいただきました 花の塔 制作 監督 沢海陽子 '
                    '音楽 かわせまき クルミ',
        'LYCOMIN': 'リコリコラジオ 安済知佳 若山詩音 あんざいちか わかやましおん '
                   '井ノ上たきな いのうえたきな 錦木千束 にしきぎちさと',
    }
