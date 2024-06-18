# from translate import Translator

# translator= Translator(to_lang="zh")
# translation = translator.translate("Force yourself to read in situations and settings when it's least convenient.")
# print(translation)
# # translate-cli -t zh "This is how many books an average CEO reads a year." -o


import os
from typing import List
import srt
# import 路径修改
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.logger_settings import api_logger
from utils.util import Util
from utils.translateQwen import *
from utils.utilSrt import replaceSentenceSysKeywordFromStr, writeSublistToFile,replaceKeywordFromFile

def translate_list_remote(preTrans:str, preTransEnSubList):
    # 尝试3次
    subZhList = []
    for i in range(0,3):
        subZhList = []
        try:
            zhContent = translate_srt_en_to_zh(preTrans)
            api_logger.info("分组翻译结果")
            api_logger.info(zhContent)

            zhSubs = srt.parse(zhContent)
            subZhList = List(zhSubs)
            
            # 分组翻译成功后，直接更新中文的时间戳，避免累积太多，视频最后都是静音
            if len(preTransEnSubList) >= len(subZhList) and len(subZhList) > 0:
                for index in range(0, len(subZhList)):
                    enSub = preTransEnSubList[index]
                    zhSub = subZhList[index]
                    if len(zhSub.proprietary) > 0:
                        api_logger.error(f"翻译错误，proprietary有内容: {zhSub.proprietary}")

                    zhSub.start = enSub.start
                    zhSub.end = enSub.end

                api_logger.info("分组翻译成功，继续下一组")
                break

        except Exception as e:
            subZhList=[]
            api_logger.error(f"翻译失败：{e}")

    # print(f"请求翻译次数{i}")
    if len(subZhList) == 0:
        api_logger.error("连续3次，字幕文件翻译成中文错误!")
        exit(1)
    
    return subZhList

def translate_srt(outSrtCnPath, inSrtFilePath, isVerticle = True):
    enAllSubList=[]
    with open(inSrtFilePath, 'r') as srcFile:
        content = srcFile.read()
        subs = srt.parse(content)
        enAllSubList = List(subs)

    zhAllSubList = []
    preTrans = ""
    enSubnList = []
    for index in range(0, len(enAllSubList)):
        enSub = enAllSubList[index]
        enSubnList.append(enSub)
        preTrans =  f"{preTrans}{enSub.index}\n{Util.format_timestamp(enSub.start.total_seconds(), always_include_hours=True)} --> {Util.format_timestamp(enSub.end.total_seconds(), always_include_hours=True)}\n{enSub.content}\n"
        if (index + 1) % 15 == 0 or index == len(enAllSubList)-1:
            api_logger.info("准备分组翻译")
            api_logger.info(preTrans)
            subZhList = translate_list_remote(preTrans, enSubnList)
            zhAllSubList = zhAllSubList + subZhList
            enSubnList=[]
            # 分组翻译重试3次
    
    writeSublistToFile(zhAllSubList, outSrtCnPath)

videoDir = "./sample"
processId = "simple5"
outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtPath = os.path.join(videoDir, f"{processId}-out.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
outSrtEnReComposePath = os.path.join(videoDir, f"{processId}-en-recompse.srt")
replaceKeyWorkTxtFilePath =  os.path.join(videoDir, f"keyword.txt")

api_logger.info(f"字幕替换关键字 {outSrtEnPath}")
replaceKeywordFromFile(outSrtEnPath, replaceKeyWorkTxtFilePath, outSrtPath)
