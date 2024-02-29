import sys
import os
import whisper
import json  # used to visualize output
from typing import Iterator, TextIO
import time
import argparse
from pathlib import Path
from combineSubtitle import *
from utils.logger_settings import api_logger
import re
import math

download_root = "./models/"


def vid_to_audio(file):
    '''extract audio from video using ffmpeg'''
    os.sys("ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn audio.mp3".format(file))
    return


def get_working_dir():
    '''get working directory'''
    working_dir = os.getcwd()
    return working_dir


def whisper_transcribe_auto_lang(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("medium", download_root=download_root, device='cuda')
    result = model.transcribe(file, fp16=False)
    json_object = json.dumps(result, indent=4)
    return result, json_object


def whisper_transcribe_en(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("medium", download_root=download_root, device='cuda')
    result = model.transcribe(file, fp16=False, language="English")
    json_object = json.dumps(result, indent=4)
    return result, json_object


def whisper_transcribe_zh(file="{}/audio.mp3".format(dir), initial_prompt="以下是普通话的句子。"):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("medium", download_root=download_root, device='cuda')

    # 简体
    result = model.transcribe(file, fp16=False, language="Chinese", initial_prompt=initial_prompt)
    # 繁体
    # result = model.transcribe(file, fp16=False, language="Chinese", initial_prompt="以下是普通話的句子。")
    json_object = json.dumps(result, indent=4)
    return result, json_object


def whisper_result_preview_json(json_object):
    '''useful for debugging, preview the result in json format, this function is not used in the main function'''
    with open("result.json", "w") as f:
        f.write(json_object)
    return


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


def split_cnsubtitle(str1: str, maxlen=22) -> str:
    """
    拆分字幕中长度超过maxlen个字的中文字幕，超过后是均分两份，每份字符数 int(总字符数/份数+0.5)。

    默认Srt.CHINESE_SUBTITLE_LENGTH，22个字符

    最多拆为5行。

    如：字符共23个,按默认22字符拆分，则拆分为2行，然后均分2份，int(23/2+0.5)=12，第一行12个字符，第二行23-12=11个字符。

    如：字符共50个,按默认22字符拆分，则拆分为3行，然后均分int(50/3+0.5)=17，第一二行17个字符，第三行50-17-17=16个字符。

    以\n为折行。

    Arguments:
        str1 -- 待拆分的字符串

    Returns:
        拆分结果
    """
    if not str1:
        return str1
    ret = str1
    strlen = len(str1)
    splite_count = math.ceil(strlen / maxlen)
    splite_len = math.ceil(strlen / splite_count)
    if splite_count == 1:
            ret = str1
    elif splite_count == 2:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:]}"
    elif splite_count == 3:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:]}"
    elif splite_count == 4:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:]}"
    elif splite_count == 5:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:splite_len*4]}\n{str1[splite_len*4:]}"

    return ret

def write_srt(transcript: Iterator[dict], file: TextIO, language:str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        if language == 'zh':
            lineStr = split_cnsubtitle(lineStr)
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}",
            file=file,
            flush=True,
        )

def whisper_result_to_srt(whisper_result, outPath="", language:str="cn"):
    '''converts whisper result to SRT format'''
    if len(outPath) == 0:
        file_name = Path(videoPath).stem
        outPath = "{}.srt".format(file_name)
    with open(outPath, "w", encoding="utf-8") as srt:
        write_srt(whisper_result["segments"], file=srt, language=language)
    return

def print_wait():
    api_logger.info("Transcribing video with Whisper... This may take long, please wait...")
    return

def addInitPrompt(srcWord:str):
    retStr = ""
    retStr = f"{retStr}书, 心理, 出版, 美文, 感官, 心灵, "
    retStr = f"{retStr}{srcWord} "
    return retStr


if __name__ == "__main__":
    '''main function'''
    api_logger.info("Getting working directory...")

    program = argparse.ArgumentParser(
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
    program.add_argument('-v', '--video', help='videoPath',
                        dest='videoPath', type=str, default='./sample/122322.mp4')
    program.add_argument('-l', '--language', help='language',
                        dest='language', type=str, default='zh')
    program.add_argument('-o', '--outPath', help='output video path',
                        dest='outPath', type=str, default='')
    program.add_argument('-t', '--audioText', help='audio text',
                        dest='audioText', type=str, default='')
    program.add_argument('-c', '--combineVideo', help='is need combine video',
                        dest='combineVideo', type=str, default='combine')
    args = program.parse_args()


    videoPath = args.videoPath
    language = args.language
    outVideoPath = args.outPath
    audioText = args.audioText
    combineVideo = args.combineVideo
    # audioText = replacePuncuation(audioText)
    audioText = addInitPrompt(audioText)
    # outSrtPath = args.outPath
    dir = get_working_dir()
    start_time = time.time()

    print_wait()
    if language == "zh":
        api_logger.info(f"模式选择: base-zh, audioText:{audioText}")
        print_wait()
        # initial_prompt
        # https://github.com/openai/whisper/discussions/963
        result, json_object = whisper_transcribe_zh(videoPath, initial_prompt=audioText)
    elif language == "en":
        api_logger.info("model selected: base-en")
        print_wait()
        result, json_object = whisper_transcribe_en(videoPath)
    else:
        result, json_object = whisper_transcribe_auto_lang(videoPath)


    api_logger.info("Turning transcription into SRT subtitle file... ")
    # if len(outSrtPath) == 0:
    file_name = Path(videoPath).stem
    os.makedirs("./out/", exist_ok=True)
    outSrtPath = "./out/{}.srt".format(file_name)
    if os.path.isfile(outSrtPath):
        os.remove(outSrtPath)
    whisper_result_to_srt(result, outPath=outSrtPath, language = language)

    end_time = time.time()
    runtime = end_time - start_time

    if combineVideo == "combine":
        if len(outVideoPath) == 0:
            outPutSubtitleMp4 = f"./out/{file_name}-sub.mp4"
        api_logger.info(f"合并视频{outVideoPath}")
        combinSubtitle(videoPath, outSrtPath, outVideoPath)

    os.system("clear")
    api_logger.info("Done! Please check the SRT file in the working directory: {}".format(dir))
    api_logger.info("Runtime: {} seconds, or {} minutes".format(runtime, runtime/60))

