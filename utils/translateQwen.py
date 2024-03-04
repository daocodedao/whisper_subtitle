
import requests
import socket
from  utils.util import Util
import json

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

serverUrl = "http://39.105.194.16:9191/v1/chat/completions/"
# localIp = getNetworkIp()
# print(f"localIp:{localIp}")
# if "192.168.0" in localIp:
#     serverUrl = "http://192.168.0.67:9191/v1/chat/completions/"


def replaceSpecialWordEnToZh(srcStr:str = None):
    if srcStr is None:
        return ""
    # 读取JSON文件
    with open("./utils/trans-en-zh-dic.json", "r") as file:
        wordList = json.load(file)
        for word in wordList:
            if word["en"] in srcStr:
                srcStr = srcStr.replace(word["en"], word["zh-cn"])

    return srcStr

def translate_en_to_zh(inSrc):
    # url = "http://39.105.194.16:9191/v1/chat/completions/"  # 替换为您要发送请求的URL
    data = {
            "systemRole": "system",
            "systemContent": "You are a helpful assistant.",
            "userRole":"role",
            "userContent":"Trump was always bothered by how Trump Tower fell 41 feet short of the General Motors building two blocks north."
    }

    systemContent = f"你是翻译助手，将后续的内容翻译成中文"

    # data["systemContent"] = systemContent
    data["systemContent"] = systemContent
    data["userContent"] = inSrc

    response = requests.post(serverUrl, json=data)

    if response.status_code == 200:
        # api_logger.info("请求成功")
        retJson = response.json()
        # api_logger.info(retJson)
        ret_text = retJson["message"]
        ret_text = replaceSpecialWordEnToZh(ret_text)
        return ret_text
    else:
        # api_logger.info("请求失败，状态码：", response.status_code)
        # api_logger.info(response.text)
        return ""

def translate_srt_en_to_zh(inSrc):
    # url = "http://39.105.194.16:9191/v1/chat/completions/"  # 替换为您要发送请求的URL
    data = {
            "systemRole": "system",
            "systemContent": "You are a helpful assistant.",
            "userRole":"role",
            "userContent":"Trump was always bothered by how Trump Tower fell 41 feet short of the General Motors building two blocks north."
    }

    systemContent = f"你是字幕翻译助手，将后续的文字块翻译成中文，输入的文字块每3行是一个整体，第一行是次序行，比如1,2,3，第二行是时间行，包括开始时间和结束时间，比如 0:00:09.180 --> 0:00:14.640，第三行是等待翻译的内容。\n输出内容次序行和时间行必须和输入块保持内容一致，行数一致，输出格式为，第一行是次序，第二行是开始时间和结束时间，第三行是翻译出的内容。不要输出额外的解释的内容。"


    # data["systemContent"] = systemContent
    data["systemContent"] = systemContent
    data["userContent"] = inSrc

    response = requests.post(serverUrl, json=data)

    if response.status_code == 200:
        # api_logger.info("请求成功")
        retJson = response.json()
        # api_logger.info(retJson)
        ret_text = retJson["message"]
        ret_text = replaceSpecialWordEnToZh(ret_text)
        return ret_text
    else:
        # api_logger.info("请求失败，状态码：", response.status_code)
        # api_logger.info(response.text)
        return ""

