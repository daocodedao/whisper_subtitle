
import srt
from translate import Translator
from utils.logger_settings import api_logger
import subprocess
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import os

videoPath="./sample/simple5.mp4 "
videoMutePath="./sample/simple5-mute.mp4 "
videoCnPath="./sample/simple5-cn.mp4 "

outSrtEnPath="./sample/simple5-en.srt"
outSrtCnPath="./sample/simple5-cn.srt"
language="en"


api_logger.info("5---------视频加上中文TTS")
folder_path = os.path.dirname(outSrtCnPath)
output_dir = os.path.join(folder_path, f"tts/")
wav_files = [f for f in os.listdir(output_dir) if f.endswith(".wav")]
wav_files = sorted(wav_files, key=int)

with open(outSrtCnPath, 'r') as srcFile:
    # 读取文件内容
    content = srcFile.read()
    subs = srt.parse(content)


command = f"ffmpeg -y -i '{videoMutePath}' "
for mp3File in wav_files:
    print(mp3File)