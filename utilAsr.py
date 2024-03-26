# 根据音频生成中文字幕

from funasr import AutoModel
from utils.logger_settings import api_logger
from typing import Iterator, TextIO


def format_milliseconds_timestamp(milliseconds: float, always_include_hours: bool = False):
    '''format timestamp to SRT format'''
    # assert seconds >= 0, "non-negative timestamp expected"
    # milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def write_srt(transcript: Iterator[dict], file: TextIO, language:str="zh"):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        # if language == 'zh':
        #     lineStr = split_cnsubtitle(lineStr)
        # api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_milliseconds_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_milliseconds_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}",
            file=file,
            flush=True,
        )

def start_zh_asr_to_srt(audioFilePath, srtFilePath):
    model = AutoModel(model="paraformer-zh",  
                    vad_model="fsmn-vad",  
                    punc_model="ct-punc-c", 
                    sentence_timestamp=True)
    resList = model.generate(input=audioFilePath, 
                        batch_size_s=300, 
                        hotword='魔搭')

    if len(resList) > 0:
        restItem = resList[0]
        with open(srtFilePath, "w", encoding="utf-8") as srt:
            write_srt(restItem["sentence_info"], srt)



