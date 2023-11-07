import json
import re
from time import sleep


def demo1():
    from app.core.utils.translate import youdao_translate
    lyco2 = 'CD62BF332309446A980443F75F9B8FE4'
    with open('test.txt', 'r', encoding='utf8') as f:
        sources = f.readlines()
        with open('单句表2无人名结果.txt', 'w+', encoding='utf8') as r:
            for i, source in enumerate(sources):
                print(f'translating {len(sources)}/{i}')
                r.write(youdao_translate(source, vocab_id=lyco2) + '\n')
                sleep(1)


def demo2():
    import openai
    openai.api_key = "sk-xxx"
    openai.api_base = "http://127.0.0.1:8000"

    target_language = "Simplified Chinese"

    subtitles = [
        '聞かせちゃいけないとは言わないですけれども',
        'まあまあ裏話的な部分だったってことですよね最初のね',
        'でもほら今日は時間がなくて',
        'いっつも言ってんな'
    ]
    previous_subtitles = []

    for i in range(len(subtitles)):
        text = subtitles[i]
        input_text = {'Input': text}
        if i + 1 < len(subtitles):
            input_text['Next'] = subtitles[i + 1]

        input_text = str(input_text)

        messages = [
            {
                'role': 'system',
                'content': f"你是一个仅用于翻译字幕文本的程序。"
                           f"你的任务是基于输入的字幕文本来输出指定语言的文字。"
                           f"禁止自行编造接下来的字幕文本内容。"
                           f"禁止回答翻译以外的任何内容。"
                           f"你将接收到需要翻译的字幕文本、之前的翻译结果、以及下一行字幕。"
                           f"如果你需要将字幕与下一行合并，仅需重复翻译一边。"
                           f"请将人物名称使用本地语言表达。"
                           f"目标语言: {target_language}"
            },
            *previous_subtitles[-4:],
            {
                'role': 'user',
                'content': input_text
            }
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        result = completion.choices[0].message['content']

        previous_subtitles.append({'role': 'user', 'content': input_text})
        previous_subtitles.append({'role': 'assistant', 'content': result})

        print('-----------------')
        print(f"{i + 1} / {len(subtitles)}")
        print("原文:", text)
        print("请求:", messages)
        print("结果:", result)


if __name__ == '__main__':
    demo2()
