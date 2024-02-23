
import requests


def translate_en_to_zh(srcText):
    
    # 外网
    # url = "http://39.105.194.16:9890/translate/en-cn/"
    
    # s 机房 /data/work/aishowos/bitwit-bot/start-translate-server.sh
    url = "http://127.0.0.1:9890/translate/en-cn/"

    data = {
        "srcLang": "en_XX",
        "dstLang": "zh_CN",
        "description": srcText
    }

    response = requests.post(url, json=data)
    # print(response)
    json_data = response.json()
    print(json_data)
    if json_data['code'] == 200:
        messge = json_data['message']
        return messge
    
    return ""
    