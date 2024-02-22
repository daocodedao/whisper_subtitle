import srt
from translate import Translator
from utils.logger_settings import api_logger
import subprocess
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import os

def format_timestamp(seconds: float, always_include_hours: bool = False):
    '''format timestamp to SRT format'''
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def whisper_transcribe_en(file="{}/audio.mp3".format(dir)):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("base")
    result = model.transcribe(file, fp16=False, language="English")
    json_object = json.dumps(result, indent=4)
    return result, json_object

def whisper_result_to_srt(whisper_result, outPath="", language:str="cn"):
    '''converts whisper result to SRT format'''
    if len(outPath) == 0:
        file_name = Path(videoPath).stem
        outPath = "{}.srt".format(file_name)
    with open(outPath, "w", encoding="utf-8") as srt:
        write_srt(whisper_result["segments"], file=srt, language=language)
    return

def write_srt(transcript: Iterator[dict], file: TextIO, language:str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}",
            file=file,
            flush=True,
        )

videoPath="./sample/simple5.mp4 "
videoMutePath="./sample/simple5-mute.mp4 "
videoCnPath="./sample/simple5-cn.mp4 "

outSrtEnPath="./sample/simple5-en.srt"
outSrtCnPath="./sample/simple5-cn.srt"
language="en"

api_logger.info("1---------视频生成英文SRT")
result, json_object = whisper_transcribe_en(videoPath)
whisper_result_to_srt(result, outPath=outSrtPath, language = language)

api_logger.info("2---------翻译中文SRT")
translator= Translator(to_lang="zh")
# outPath='./sample/simple5-cn.srt'
with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
    with open(outSrtEnPath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        for sub in subs:
            translation = translator.translate(sub.content)
            print(translation)
            print(f"start second:{sub.start.total_seconds()} end:{sub.end.total_seconds()}")
            print(
                f"{sub.index}\n"
                f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                f"{translation}",
                file=outFile,
                flush=True,
            )


api_logger.info("3---------中文SRT转TTS")
command=f"/data/work/GPT-SoVITS/start-gen-voice-local.sh -l 'zh'  -s '{outSrtCnPath}' "
api_logger.info(f"命令：")
api_logger.info(command)
result = subprocess.check_output(command, shell=True)


api_logger.info("4---------原视频静音")
command=f"ffmpeg -i '{videoPath}' -c copy -an {videoMutePath}"
api_logger.info(f"命令：")
api_logger.info(command)
result = subprocess.check_output(command, shell=True)


api_logger.info("5---------视频加上中文TTS")
folder_path = os.path.dirname(outSrtCnPath)
output_dir = os.path.join(folder_path, f"tts/")
wav_files = [f for f in os.listdir(output_dir) if f.endswith(".wav")]
wav_files = sorted(wav_files)

with open(outSrtCnPath, 'r') as srcFile:
    # 读取文件内容
    content = srcFile.read()
    subs = srt.parse(content)


command = f"ffmpeg -y -i '{videoMutePath}' "
for mp3File in wav_files:


# ffmpeg -y -i video.mp4 -itsoffset 10 -i note1.mp3 -itsoffset 15 -i note2.mp3 -itsoffset 90.7 -i note3.mp3 -itsoffset 120.58 -i note4.mp3 -filter_complex amix=inputs=5[a] -map 0:v -map [a] -c:v copy -async 1 -c:a aac output.mp4

