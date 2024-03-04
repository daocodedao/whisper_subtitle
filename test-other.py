
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


# videoDir = "/Users/linzhiji/Downloads/Abt7FwZwY/"
videoDir = "/data/work/translate/Downloads/Abt7FwZwY/"


videoId = "Abt7FwZwY"
videoPath=f"{videoDir}{videoId}.mp4"
videoMutePath=f"{videoDir}{videoId}-mute.mp4"
videoCnPath=f"{videoDir}{videoId}-cn.mp4"

outSrtEnPath=f"{videoDir}{videoId}-en.srt"
outSrtCnPath=f"{videoDir}{videoId}-cn.srt"
language="en"

combine_mp3_path = f"{videoDir}{videoId}-combine.mp3"
combine_mp3_speed_path = f"{videoDir}{videoId}-combine-speed.mp3"


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
    curAudioFileDuration = Util.getMediaDuration(audioFilePath)
    sub = subList[index]
    timeDiff = sub.end.total_seconds() - sub.start.total_seconds()
    print(f"当前{audioFilePath} 中文音频时长: {curAudioFileDuration} srt时长:{timeDiff}  srt时长-中文音频:{timeDiff-curAudioFileDuration}")

    # 判断是否需要加入静音
    print(f"当前字幕开始时间: {sub.start.total_seconds()} 已经合并的音频时长:{totalGenDuration}")
    if sub.start.total_seconds() > totalGenDuration:
        silence_duration = (sub.start.total_seconds() - totalGenDuration)*1000
        api_logger.info(f"需要加入静音音频， 时长：{silence_duration/1000}秒")
        second_of_silence = AudioSegment.silent(duration=silence_duration)
        api_logger.info(f"加入前时长：{combined.__len__()/1000}")
        combined = combined + second_of_silence
        api_logger.info(f"加入后时长：{combined.__len__()/1000}")
        curAudioFileDuration = curAudioFileDuration + silence_duration/1000

    # srt当前总时间长
    totalSrtDuraton = totalSrtDuraton + timeDiff

    totalGenDuration = totalGenDuration + curAudioFileDuration
    audioFile_speed_dir = os.path.join(folder_path, f"tts-speed/")
    sound = AudioSegment.from_file(audioFilePath, format="wav")
    
    if combined is None:
        combined = sound
    else:
        combined = combined + sound


file_handle = combined.export(combine_mp3_path, format="mp3")


combine_mp3_duration = Util.getMediaDuration(combine_mp3_path)
video_duration = Util.getMediaDuration(videoMutePath)
api_logger.info(f"判断是否需要变速, combine_mp3_duration={combine_mp3_duration} video_duration={video_duration}")
if combine_mp3_duration > video_duration:
    api_logger.info(f"视频需要变速, {combine_mp3_duration/video_duration}")
    speed_change(combine_mp3_path, combine_mp3_speed_path, combine_mp3_duration/video_duration)
    combine_mp3_path = combine_mp3_speed_path



cmd = f'ffmpeg -y -i {videoMutePath} -i {combine_mp3_path} -c:v copy -c:a aac {videoCnPath}'
subprocess.call(cmd, shell=True)                                    
print(f'Mixing Done: {videoCnPath}')
