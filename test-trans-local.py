
from utils.logger_settings import api_logger
from utils.translateBaidu import *
import srt
from utils.translateQwen import *
from utils.replaceKeyword import *


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



def translate_srt(outSrtCnPath, outSrtEnPath, isVerticle = True):

    with open(outSrtEnPath, 'r') as srcFile:
        content = srcFile.read()
        subs = srt.parse(content)
        subList = []
        for sub in subs:
            subList.append(sub)

        zhSubList = []
        for i in range(0,3):
            zhSubList = []
            try:
                api_logger.info(f"准备第{i}次翻译")

                preTrans = ""
                for index in range(0, len(subList)):
                   enSub = subList[index]
                   preTrans =  f"{preTrans}{enSub.index}\n{format_timestamp(enSub.start.total_seconds(), always_include_hours=True)} --> {format_timestamp(enSub.end.total_seconds(), always_include_hours=True)}\n{enSub.content}\n"
                   if (index + 1) % 15 == 0 or index == len(subList)-1:
                    zhContent = translate_srt_en_to_zh(preTrans)
                    api_logger.info(zhContent)
                    zhSubs = srt.parse(zhContent)
                    for zhSub in zhSubs:
                        zhSubList.append(zhSub)
                    preTrans = ""

                if len(subList) >= len(zhSubList):
                    # api_logger.error("字幕文件翻译成中文错误，两个字幕行数不一样")
                    break
            except Exception as e:
                api_logger.error(f"翻译失败：{e}")
                # exit(1)
        if i == 3:
            api_logger.error("连续3次，字幕文件翻译成中文错误，两个字幕行数不一样")
            exit(1)

        with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
            for index in range(0, len(zhSubList)):
                enSub = subList[index]
                zhSub = zhSubList[index]

                zhContent = zhSub.content
                zhContent = replaceSentenceWithKeyword(zhContent)

                print(
                    f"{enSub.index}\n"
                    f"{format_timestamp(enSub.start.total_seconds(), always_include_hours=True)} --> "
                    f"{format_timestamp(enSub.end.total_seconds(), always_include_hours=True)}\n"
                    f"{zhContent}",
                    file=outFile,
                    flush=True,
                )



outSrtEnPath = "./sample/wbHUdEeVeDU-en.srt"
outSrtCnPath = "./sample/wbHUdEeVeDU-cn.srt"

translate_srt(outSrtCnPath, outSrtEnPath)