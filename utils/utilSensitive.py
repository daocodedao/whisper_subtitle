import time
import jieba
import os
import spacy
from spacy import displacy
import spacy.cli
import os,time
from typing import List
import srt
# import 路径修改
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.logger_settings import api_logger
from utils.util import Util

sensitive_word_detector = None
NER = None

def load_en_sensitive_words():
    global sensitive_word_detector
    print(os.getcwd())
    # 从文件加载敏感词列表
    sensitive_word_detector = set()
    with open('utils/sensitive_words_lines_en.txt', 'r') as file:
        for line in file:
            line = line.strip()  # 去除换行符和空格
            sensitive_word_detector.add(line)
    
    # print(f"load_sensitive_file cost is {str((time.time() - load_file_st)*1000)[:6]} ms")

def detectSensitiveByNLP(text:str): 
    global NER
    api_logger.info(f"开始NLP检测 {text}")

    try:
        if not NER:
            NER = spacy.load("en_core_web_sm")
    except OSError as e:
        spacy.cli.download("en_core_web_sm")
        # time.sleep(5)

    nerSet = set()
    text = NER(text)
    for word in text.ents:
        nerSet.add(word.text)
        # 去掉单词里的空格
        nerSet.add(word.text.replace(" ", ""))
        # 转为小写
        nerSet.add(word.text.replace(" ", "").lower())
        # print(word.text,word.label_)

    for word in nerSet:
        if word in sensitive_word_detector:
            api_logger.info(f"{text} NLP检测包含敏感词 {word}")
            return True, word

    return False, ""

def detectSensitiveFromStr(text: str):
    # api_logger.info(f"检测字符串： {text}")
    global sensitive_word_detector
    if not sensitive_word_detector:
        load_en_sensitive_words()
    api_logger.info(f"开始分词检测")
    for word in jieba.cut(text):
        if word in sensitive_word_detector:
            api_logger.info(f"{text} 分词检测包含敏感词 {word}")
            return True, word

    isDetect, detectWord = detectSensitiveByNLP(text)
    return isDetect, detectWord

def detectSensitiveFromFile(filePath: str):
    if not os.path.exists(filePath):
        return False
    
    with open(filePath, "r") as file:
        content = file.read()
        isDetect, detectWord =  detectSensitiveFromStr(content)
        return isDetect, detectWord


def detectSensitiveFromSrt(filePath: str):
    if not os.path.exists(filePath):
        return False

    with open(filePath, 'r') as srcFile:
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)
        for sub in subList:
            curLineContent = sub.content
            isDetect, isDetect =  detectSensitiveFromStr(curLineContent)
            return isDetect, isDetect
    return False, ""


# 提取英文敏感词到独立文件
def distributeEnSensitive():
    # 从文件加载敏感词列表
    sensitive_word_detector = set()
    with open('utils/sensitive_words_lines_all.txt', 'r') as file:
        for line in file:
            line = line.strip()  # 去除换行符和空格
            srcLang = Util.detect_language_with_langdetect(line)
            if srcLang != "zh":
                sensitive_word_detector.add(line)

    with open('utils/sensitive_words_lines_en.txt', "w") as file:
        for item in sensitive_word_detector:
            file.write(item + "\n")

# 去重
def deduplicationSensitive():
    # 从文件加载敏感词列表
    sensitive_word_detector = set()
    with open('utils/sensitive_words_lines_all.txt', 'r') as file:
        for line in file:
            line = line.strip()  # 去除换行符和空格
            # srcLang = Util.detect_language_with_langdetect(line)
            # if srcLang == "en":
            sensitive_word_detector.add(line)

    with open('utils/sensitive_words_lines_all.txt', "w") as file:
        for item in sensitive_word_detector:
            file.write(item + "\n")

if __name__ == "__main__":
    print(distributeEnSensitive())

    # line = "xijingpin"
    # srcLang = Util.detect_language_with_langdetect(line)
    # print("done")

