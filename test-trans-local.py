import hashlib
import requests
import time
import json

appKey = "5A77CE4169854865B7D3714BD39A78C6"
param = {
    "textList": ["Trump was always bothered by how Trump Tower fell 41 feet short of the General Motors building two blocks north."],
    "appId": "FFFFB26AF7A64AB59620240229114219",
    "domain": "default",
    "from": "en",
    "to": "zh"
}
ts = str(int(time.time() * 1000))

concatString = appKey + json.dumps(param) + ts
secretKey = hashlib.md5(concatString.encode()).hexdigest()

url = "https://translate.10jqka.com.cn/translateApi/batch/v2/get/result"
body = {
    "param": json.dumps(param),
    "secretKey": secretKey,
    "ts": ts
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(url, data=body, headers=headers)
if response.status_code == 200:
    print(response.text)
else:
    print("Request failed with response code:", response.status_code)