
import srt
from translate import Translator
from utils.logger_settings import api_logger
import subprocess
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import os
from utils.util import Util
from pydub import AudioSegment
import ffmpeg
import numpy as np
import librosa
import soundfile as sf
from scipy.io import wavfile



videoPath="./sample/simple5.mp4"
videoMutePath="./sample/simple5_mute.mp4"
videoCnPath="./sample/simple5-cn.mp4"

outSrtEnPath="./sample/simple5-en.srt"
outSrtCnPath="./sample/simple5-cn.srt"
language="en"

combine_mp3_path = "./sample/simple5-combine.mp3"
combine_mp3_speed_path = "./sample/simple5-combine-speed.mp3"


def speed_change(input_file, output_file, speedRate:float = 1.0):
    song, fs = librosa.load(input_file)
    song_2_times_faster = librosa.effects.time_stretch(song, rate=speedRate)
    wavfile.write(output_file, fs, song_2_times_faster) # save the song


api_logger.info("5---------视频加上中文TTS")
folder_path = os.path.dirname(outSrtCnPath)
output_dir = os.path.join(folder_path, f"tts/")
wav_files = [f for f in os.listdir(output_dir) if f.endswith(".wav")]
# wav_files = wav_files.sorted(wav_files, key=lambda fname: int(fname.split('.')[0]))
wav_files.sort(key=lambda x: '{0:0>8}'.format(x))

subList = []
with open(outSrtCnPath, 'r') as srcFile:
    # 读取文件内容
    content = srcFile.read()
    subs = srt.parse(content)
    for sub in subs:
        subList.append(sub)

print(len(subList))

command = f"ffmpeg -y -an -i '{videoMutePath}' "
filterCommand = "-filter_complex amix -map 0:v"
# index = 0
combined = None
totalSrtDuraton = 0
totalGenDuration = 0
for audioFile in wav_files:

    file_name_without_ext = os.path.splitext(os.path.basename(audioFile))[0]
    index = int(file_name_without_ext) - 1
    if index >= len(subList):
        continue

    audioFilePath = f"{output_dir}{audioFile}"
    genAudioDuration = Util.getMediaDuration(audioFilePath)
    sub = subList[index]
    timeDiff = sub.end.total_seconds() - sub.start.total_seconds()
    print(f"中文音频时长: {genAudioDuration} srt时长:{timeDiff}  srt时长-中文音频:{timeDiff-genAudioDuration}")

    # 判断是否需要加入静音
    print(f"当前字幕开始时间: {sub.start.total_seconds()} 已经合并的音频时长:{totalGenDuration}")
    if sub.start.total_seconds() > totalGenDuration:
        silence_duration = (sub.start.total_seconds() - totalGenDuration)*1000
        api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
        second_of_silence = AudioSegment.silent(duration=silence_duration)
        scombined = combined + second_of_silence

    totalSrtDuraton = totalSrtDuraton + timeDiff
    totalGenDuration = totalGenDuration + genAudioDuration
    audioFile_speed_dir = os.path.join(folder_path, f"tts-speed/")
    sound = AudioSegment.from_file(audioFilePath, format="wav")
    
    if combined is None:
        combined = sound
    else:
        combined = combined + sound


file_handle = combined.export(combine_mp3_path, format="mp3")

api_logger.info("判断是否需要变速")
combine_mp3_duration = Util.getMediaDuration(combine_mp3_path)
video_duration = Util.getMediaDuration(videoMutePath)
if combine_mp3_duration > video_duration:
    api_logger.info("视频需要变速")
    speed_change(combine_mp3_path, combine_mp3_speed_path, combine_mp3_duration/video_duration)
    combine_mp3_path = combine_mp3_speed_path



cmd = f'ffmpeg -y -i {videoMutePath} -i {combine_mp3_path} -c:v copy -c:a aac {videoCnPath}'
subprocess.call(cmd, shell=True)                                    
print(f'Mixing Done: {videoCnPath}')
