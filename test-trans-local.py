import hashlib
import requests
import time
import json

from utils.translateBaidu import *


retStr = replaceSpecialWordEnToZh("这笔交易很复杂。Conseco投资2.11亿美元，Trump出资1100万美元，")

print(retStr)