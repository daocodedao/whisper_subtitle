
import requests
import socket

import json
from utils.logger_settings import api_logger

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

serverUrl = "http://39.105.194.16:9191/v1/chat/completions/"
kRequestTimeout = 60*2


def composeV1Dic(systemContent, userContent):
    return {
         "model": "Qwen/Qwen2-7B-Instruct",
         "messages":[{
            "role": "system",
            "content": systemContent,
            },
            {
            "role":"user",
            "content":userContent
            }]
    }

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

    systemContent = f"你是翻译助手，将后续的内容翻译成中文"
    jsonData = composeV1Dic(systemContent=systemContent, userContent=inSrc)

    response = requests.post(serverUrl, json=jsonData, timeout=kRequestTimeout)

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

def translate_srt_en_to_zh(inSrc, inNewTransLate=True):

    systemContent = f"你是字幕翻译助手，将后续的文字块里的英文翻译成中文，每次翻译都是全新的内容，不用参考之前的内容。输入的文字每3行是一个文字块，第1行是次序行，第2行是时间行，第3行是需要翻译的英文内容。\n输出格式要求：\n1.次序行和时间行必须和输入保持内容一致，行数一致\n2.只有第3行需要翻译，第3行是翻译出的内容\n3.不要输出额外的解释的内容，不要输出备注内容，不要输出额外内容。\n4.专业的名词不要翻译\n5.如果文字块内容无法翻译，则直接跳过整个文字块，输出是不显示该文字块，继续下一个文字块\n6.翻译后的文案要符合中文习惯\n7.英文中类似 喜欢视频，订阅视频，翻译为 点赞关注我们\n8.'stable diffusion', 'token' 这几个英文单词不翻译成中文 \n\n\n输入内容参考：\n1\n0:00:00.000 --> 0:00:05.020\nHave you ever wondered who is behind the financing of Saudi Arabia's crazy mega projects?\n2\n0:00:05.380 --> 0:00:09.060\nIt is the richest family in the world, and you've never even heard of them.\n3\n0:00:09.180 --> 0:00:14.640\nThey have gold toilets, gold Lamborghinis, and even purchased the world's most expensive house,\n  输出内容参考：\n1\n0:00:00.000 --> 0:00:05.020\n你有没有想过沙特阿拉伯那些疯狂大项目背后的资助者是谁？\n2\n0:00:05.380 --> 0:00:09.060\n答案是全球最富有的家族，但他们鲜为人知。\n3\n0:00:09.180 --> 0:00:14.640\n他们有镀金马桶、定制的黄金兰博基尼，甚至买下了世上最贵的房子,\n"
    jsonData = composeV1Dic(systemContent=systemContent, userContent=inSrc)

    response = requests.post(serverUrl, json=jsonData, timeout=kRequestTimeout)
    api_logger.info(f"请求翻译 {serverUrl} {jsonData}")
    api_logger.info(f"返回结果： {response}")
    if response.status_code == 200:
        # api_logger.info("请求成功")
        retJson = response.json()
        # api_logger.info(retJson)
        ret_text = retJson["message"]
        ret_text = replaceSpecialWordEnToZh(ret_text)
        return ret_text
    else:
        api_logger.error("请求失败，状态码：", response.status_code)
        api_logger.error(response.text)
        return ""

