import srt
import json
import re
from utils.logger_settings import api_logger
from  utils.util import Util

gKeyWordList = []
def replaceSentenceSysKeywordFromStr(srcStr:str = None):
    global gKeyWordList
    if len(gKeyWordList) == 0:
        gKeyWordList = readKeyWordPairFromJson("./utils/trans-keyword-replace.json")
    
    if srcStr is None:
        return ""

    for word in gKeyWordList:
        if word["key-word"] in srcStr:
            srcStr = word["replace-word"]
            return srcStr
    return srcStr

def writeSublistToFile(zhAllSublist, outSrtCnPath, isNeedReplaceSysKeyWord=True):
    api_logger.info(f"写回文件：{outSrtCnPath}")
    with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
        for index,sub in  enumerate(zhAllSublist):
            srcContent = sub.content
            if isNeedReplaceSysKeyWord:
                srcContent = replaceSentenceSysKeywordFromStr(srcContent)
            print(
                f"{index + 1}\n"
                f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                f"{srcContent}",
                file=outFile,
                flush=True,
            )

def readKeyWordPairFromTxt(replacekeyWordTxtFilePath):
    replaceKeyDicList = []
    with open(replacekeyWordTxtFilePath, 'r') as replaceFile:
        replacekeyWordList = replaceFile.readlines()
        for replacekeyWord in replacekeyWordList:
            parts_by_comma = replacekeyWord.split('--->')
            if parts_by_comma and len(parts_by_comma)==2:
                replaceKeyDicList.append({
                    'key-word': parts_by_comma[0].strip(),
                    'replace-word': parts_by_comma[1].strip()
                })
    return replaceKeyDicList

def readKeyWordPairFromJson(replacekeyWordJsonFilePath):
    with open(replacekeyWordJsonFilePath, "r") as file:
        wordList = json.load(file)
        return wordList

def readSrtListFromFile(srtFilePath):
    with open(srtFilePath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)
        if len(subList) == 0:
            return []
        else:
            return subList

def replace_ignore_case(text, pattern, replacement):
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)


def replaceSublistFromKeyWordDic(subList, keyWordList):
    for sub in subList:
        for keyWord in keyWordList:
            # if keyWord["key-word"] in sub.content:
            sub.content = replace_ignore_case(sub.content, keyWord["key-word"], keyWord["replace-word"])
                # sub.content = sub.content.replace(keyWord["key-word"], keyWord["replace-word"])

def replaceKeywordFromFile(inSrtPath, replacekeyWordTxtFilePath, outSrtPath):
    subList = readSrtListFromFile(inSrtPath)
    replaceKeyDicList = readKeyWordPairFromTxt(replacekeyWordTxtFilePath)

    replaceSublistFromKeyWordDic(subList, replaceKeyDicList)

    writeSublistToFile(subList, outSrtPath, isNeedReplaceSysKeyWord=False)
