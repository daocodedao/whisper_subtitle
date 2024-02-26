
import requests
import socket
from  utils.util import Util

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


def translate_en_to_zh(srcText):
    url = "http://192.168.31.69:9890/translate/en-cn/"
    # 外网
    if Util.isMac():
        url = "http://39.105.194.16:9890/translate/en-cn/"
    else:
        localIp = getNetworkIp()
        print(f"localIp:{localIp}")
        if "192.168.0.69" in localIp:
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
    