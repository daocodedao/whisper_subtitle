
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
from utils.util import Util


def write_srt(transcript: Iterator[dict], file: TextIO, language: str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{Util.format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{Util.format_timestamp(segment['end'], always_include_hours=True)}\n"
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

def split_by_punctuations(instr, punctuations: list[str] = [",",".","?"]):
    line1Str = ""
    line2Str = instr

    if instr is None or len(instr) == 0:
        return line1Str, line2Str
    
    for punctuation in punctuations:
        if punctuation in instr :
            position = instr.find(punctuation)
            if position == len(instr) - 1:
                continue

            line1Str = instr[:position+1]
            line2Str = instr[position+2:]
            return line1Str, line2Str

    # 第二行没有找到标点符号，整体挪到上一行
    line1Str = instr
    line2Str = ""        
    return line1Str, line2Str



def recom_en_srt(inSrcFilePath, outSrcFilePath):
    # translator = Translator(to_lang="zh")
    # outPath='./sample/simple5-cn.srt'
    isModified = False
    with open(outSrcFilePath, "w", encoding="utf-8") as outFile:
        with open(inSrcFilePath, 'r') as srcFile:
            # 读取文件内容
            content = srcFile.read()
            subs = srt.parse(content)
            subList = []
            for sub in subs:
                subList.append(sub)

            curHandleLine = -1
            lineIdx = 1
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
                    isModified = True
                    nextLineContent = subList[index + 1].content
                    line1, line2 = split_by_punctuations(nextLineContent)
                    if len(line1) > 0:
                        line1 = curLineContent + " " + line1
                    else:
                        line1 = curLineContent
                        isModified = False


                    if len(line2) > 0:
                        # 准备写2行
                        # 第一行
                        api_logger.info(line1)
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                            f"{line1}",
                            file=outFile,
                            flush=True,
                        )
                        lineIdx = lineIdx + 1

                        index = index + 1
                        sub = subList[index]
                        api_logger.info(line2)
                        curHandleLine = index
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                            f"{line2}",
                            file=outFile,
                            flush=True,
                        )
                        lineIdx = lineIdx + 1
                    else:
                        index = index + 1
                        curHandleLine = index

                        nextLineSub = subList[index]
                        curLineEndTime = nextLineSub.end.total_seconds()
                        
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(curLineEndTime, always_include_hours=True)}\n"
                            f"{line1}",
                            file=outFile,
                            flush=True,
                        )
                            
                else:
                    api_logger.info(sub.content)
                    print(
                        f"{lineIdx}\n"
                        f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{sub.content}",
                        file=outFile,
                        flush=True,
                    )
                    lineIdx = lineIdx + 1
    
    return isModified

def loopHandleEn_srt(inSrcFilePath, outSrcFilePath):
    while(True):
        isModified = recom_en_srt(inSrcFilePath, outSrcFilePath)
        if not isModified:
            break
        # 打开文件a并读取其内容
        with open(outSrcFilePath, 'r') as file_a:
            content_a = file_a.read()

        # 打开文件b并写入内容_a
        with open(inSrcFilePath, 'w') as file_b:
            file_b.write(content_a)


videoPath="sample/wbHUdEeVeDU.mp4"
videoDir = os.path.dirname(videoPath)
processId="wbHUdEeVeDU"
outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
language = "en"

api_logger.info("1---------视频生成英文SRT")
# result, json_object = whisper_transcribe_en(videoPath)
# whisper_result_to_srt(result, outPath=outSrtEnPath, language=language)
outSrtEnRePath = os.path.join(videoDir, f"{processId}-en-re.srt")
loopHandleEn_srt(outSrtEnPath, outSrtEnRePath)


# api_logger.info("2---------翻译中文SRT")
# try:
#     translate_srt(outSrtCnPath, outSrtEnPath)
# except Exception as e:
#     api_logger.error(f"翻译失败：{e}")
#     exit(1)
