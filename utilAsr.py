from funasr import AutoModel
from utils.logger_settings import api_logger
from typing import Iterator, TextIO
import math

def format_timestamp(milliseconds: float, always_include_hours: bool = False):
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

# def split_cnsubtitle(str1: str, maxlen=22) -> str:
#     """
#     拆分字幕中长度超过maxlen个字的中文字幕，超过后是均分两份，每份字符数 int(总字符数/份数+0.5)。

#     默认Srt.CHINESE_SUBTITLE_LENGTH，22个字符

#     最多拆为5行。

#     如：字符共23个,按默认22字符拆分，则拆分为2行，然后均分2份，int(23/2+0.5)=12，第一行12个字符，第二行23-12=11个字符。

#     如：字符共50个,按默认22字符拆分，则拆分为3行，然后均分int(50/3+0.5)=17，第一二行17个字符，第三行50-17-17=16个字符。

#     以\n为折行。

#     Arguments:
#         str1 -- 待拆分的字符串

#     Returns:
#         拆分结果
#     """
#     if not str1:
#         return str1
#     ret = str1
#     strlen = len(str1)
#     splite_count = math.ceil(strlen / maxlen)
#     splite_len = math.ceil(strlen / splite_count)
#     if splite_count == 1:
#             ret = str1
#     elif splite_count == 2:
#             ret = f"{str1[0:splite_len]}\n{str1[splite_len:]}"
#     elif splite_count == 3:
#             ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:]}"
#     elif splite_count == 4:
#             ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:]}"
#     elif splite_count == 5:
#             ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:splite_len*4]}\n{str1[splite_len*4:]}"

#     return ret

def write_srt(transcript: Iterator[dict], file: TextIO, language:str="zh"):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        # if language == 'zh':
        #     lineStr = split_cnsubtitle(lineStr)
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
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



