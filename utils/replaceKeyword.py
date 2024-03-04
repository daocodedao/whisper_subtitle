
from  utils.util import Util
import json

def replaceSentenceWithKeyword(srcStr:str = None):
    if srcStr is None:
        return ""
    # 读取JSON文件
    with open("./utils/trans-ignore.json", "r") as file:
        wordList = json.load(file)
        for word in wordList:
            if word["key-word"] in srcStr:
                srcStr = word["replace-word"]
                break

    return srcStr