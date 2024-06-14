import requests
import os
# import 路径修改
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.util import Util
from utils.logger_settings import api_logger
from taskConfig import getVideoSearchAPI, needSplitFromStartId
from model.videoInfo import LongVideo, ShortVideo

async def searchVideoFromApi(segmentKeywords, searchCount=10, isHorizon=True, fromCategory="all"):
    url = getVideoSearchAPI()
    kRequestTimeout = 60*2
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    if not fromCategory:
        fromCategory = "all"
        
    paraDic = {
        "keyword":segmentKeywords,
        "searchCount":searchCount,
        "isHorizon":int(isHorizon),
        "fromCategory":fromCategory,
    }
    api_logger.info(f"搜索视频 {segmentKeywords} searchCount={searchCount} isHorizon={isHorizon} fromCategory={fromCategory}")

    resp = requests.post(url=url, json=paraDic, timeout=kRequestTimeout) 
    result = resp.json()
    api_logger.info(f"result: {result}")
    if result['code'] == 200:
        dicList = result['message']
        if dicList and len(dicList) > 0:
            shorVideoList = [ShortVideo.model_validate(user_dict) for user_dict in dicList]
            return shorVideoList
        else:
            return []
    else:
        return []

# if __name__ == "__main__":
    # searchVideo("The men are standing around the hole")
