
import json



def replaceSpecialWordEnToZh(srcStr:str = None):
    if srcStr is None:
        return ""
    # 读取JSON文件
    with open("trans-en-zh-dic.json", "r") as file:
        wordList = json.load(file)
        for word in wordList:
            if word["en"] in srcStr:
                srcStr = srcStr.replace(word["en"], word["zh-cn"])

    return srcStr

