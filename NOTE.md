
## WhisperNote

### 微调模型的思路

#### 没有 audio-text pair

使用initial prompt，为特定词汇强化log-probs
参考

- https://github.com/openai/whisper/discussions/117#discussioncomment-3727051
- https://github.com/openai/whisper/blob/0f39c89d9212e4d0c64b915cf7ba3c1f0b59fecc/whisper/transcribe.py#L270

#### 有 audio-text pair

https://huggingface.co/blog/fine-tune-whisper

#### 对话人标注实现

https://github.com/openai/whisper/discussions/104#discussioncomment-3952649

### 微调后

whisper.cpp repo的model目录下有工具  
可以将pickle格式的`pt`文件转成ggml格式的`bin`文件

### 最终步骤

1. 准备好补充文本来源的日语字幕和视频
2. 视频去背景音，使用 https://github.com/facebookresearch/demucs
3. 根据字幕时间戳切片并标注
4. 训练
5. 测试

FFmpegNote
--
### 裁剪
```bash
ffmpeg 
  -ss 30 # start seconds
  -i input.mp4
  -c copy # -codec "just copy" instead of "decode->filter->encode"
  -t 10 # extract next 10 seconds, or "-to 40" for exact timestamp
  output.mp4
```

ChatGPTPrompt
--
### Test1
翻译测试
```
我需要你帮我翻译一段对话。
接下来，我会先发送一段术语表。
然后，我会发送两个人的对话。
请你参考术语表，并结合对话中的上下文，将对话从日文翻译为中文。
你准备好了吗？
```

```
以下是术语表
リコリス・リコイル:Lycoris Recoil
リコリス:Lycoris
リコリコ:LycoReco
リコリコラジオ:LycoReco Radio
リコラジ:莉可莉可广播
りこりす・りこいる:Lycoris Recoil
りこりす:Lycoris
りこりこ:LycoReco
りこりこラジオ:LycoReco Radio
りこラジ:莉可莉可广播
錦木千束:锦木千束
にしきぎ　ちさと:锦木千束
安済知佳:安济知佳
あんざい　ちか:安济知佳
井ノ上たきな:井上泷奈
いのうえ　たきな:井上泷奈
若山詩音:若山诗音
わかやま　しおん:若山诗音
```

```
发送对话
```

### Test2
润色测试
```
在我发送任意内容后，你需要将内容改写为更加自然且更加简短的句式。
如果内容已经足够自然而无需改写，你需要返回 “无需改写”
如果我发送的内容以 “//” 开头，你需要将内容记住并作为改写内容的参考
你准备好了吗？
```

### Test3
翻译测试
```
请帮我翻译日文对话。
当我发送任意日文对话，你需要将内容翻译为中文，并且尽可能使用自然且简短的句式。
如果我发送的内容以 “//” 开头，你需要将内容作为之后的翻译参考，并返回“记忆成功”。
你准备好了吗？
```
```
//りこりこラジオ:LycoReco Radio
```