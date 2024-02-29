
from whisper.utils import get_writer
from utils.logger_settings import api_logger
import whisper
import json
import os
from typing import Iterator, TextIO
from pathlib import Path
import srt
from utils.translateBaidu import *
from combineSubtitle import *
import re
from collections import Counter

def format_timestamp(seconds:float, always_include_hours: bool = False):
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


def write_srt(transcript: Iterator[dict], file: TextIO, language: str):
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


def whisper_result_to_srt(whisper_result, outPath="", language: str = "cn"):
    '''converts whisper result to SRT format'''
    if len(outPath) == 0:
        file_name = Path(videoPath).stem
        outPath = "{}.srt".format(file_name)
    with open(outPath, "w", encoding="utf-8") as srt:
        write_srt(whisper_result["segments"], file=srt, language=language)
    return


def whisper_transcribe_en(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("medium", download_root=download_root, device='cuda')

    # result = model.transcribe(file, fp16=False, language="English")
    # init_prompt = "Umm, let me think like, like, thinking."
    init_prompt = "Umm, let me think like, hmm... Okay, here's what I'm, like, thinking."

    result = model.transcribe(file, fp16=False, language="English", word_timestamps=True, initial_prompt=init_prompt)
    json_object = json.dumps(result, indent=4)
    return result, json_object

def get_substring(string, percentage):
    length = int(len(string) * percentage)
    return string[:length]

def get_from_substring(string, percentage):
    length = int(len(string) * percentage)
    return string[length:]

def translate_srt(outSrtCnPath, outSrtEnPath):
    # translator = Translator(to_lang="zh")
    # outPath='./sample/simple5-cn.srt'
    with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
        with open(outSrtEnPath, 'r') as srcFile:
            # 读取文件内容
            content = srcFile.read()
            subs = srt.parse(content)
            subList = []
            for sub in subs:
                subList.append(sub)

            curHandleLine = -1
            for index in range(0, len(subList)):
                if index == curHandleLine:
                    continue
                sub = subList[index]
                append_punctuations: str = "?.,"
                # 最后一个字符不是标点符号
                curLineContent = sub.content
                lastChar = curLineContent[len(curLineContent) - 1]

                # 结尾不是标点符号, 准备连续操作两行
                if len(curLineContent) > 0 and lastChar not in append_punctuations and index + 1 < len(subList):
                    curLineCharCount = Counter(curLineContent)
                    nextLineContent = subList[index + 1].content
                    nextLineCharCount = Counter(nextLineContent)
                    waitTran = curLineContent + " " + nextLineContent
                    translation = translate_en_to_zh(waitTran)
                    api_logger.info(waitTran)
                    api_logger.info(translation)

                    # 准备写2行
                    # 第一行
                    line1Per = curLineCharCount.total()/(curLineCharCount.total()+nextLineCharCount.total())
                    translationLine1 = get_substring(translation, line1Per)
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translationLine1}",
                        file=outFile,
                        flush=True,
                    )

                    index = index + 1
                    curHandleLine = index
                    sub = subList[index]
                    translationLine1 = get_from_substring(translation, line1Per)
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translationLine1}",
                        file=outFile,
                        flush=True,
                    )
                            
                else:
                    # index = index + 1
                    translation = translate_en_to_zh(sub.content)
                    api_logger.info(sub.content)
                    api_logger.info(translation)
                    # api_logger.info(f"start second:{sub.start.total_seconds()} end:{sub.end.total_seconds()}")
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translation}",
                        file=outFile,
                        flush=True,
                    )



videoPath="/data/work/translate/p0X4mhxQpjU/p0X4mhxQpjU.mp4"
videoDir = os.path.dirname(videoPath)
processId="p0X4mhxQpjU"
outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
language = "en"

api_logger.info("1---------视频生成英文SRT")
result, json_object = whisper_transcribe_en(videoPath)
whisper_result_to_srt(result, outPath=outSrtEnPath, language=language)



# api_logger.info("2---------翻译中文SRT")
# try:
#     translate_srt(outSrtCnPath, outSrtEnPath)
# except Exception as e:
#     api_logger.error(f"翻译失败：{e}")
#     exit(1)
