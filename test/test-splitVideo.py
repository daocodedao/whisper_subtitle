
import os,sys
# import 路径修改
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.logger_settings import api_logger
from utils.util import Util
from utils.mediaUtil import MediaUtil
from utils.splitVideo import splitVideoFastByPath


def getVideoPathsFromDir(fromDir):
    if os.path.exists(fromDir) == False:
        return []
    else:
        videoList = [os.path.join(fromDir, f) for f in os.listdir(fromDir) if f.endswith(".mp4")]
        videoList = sorted(videoList)    
        return videoList


processId="dya1cv9FTMo"
videoDir=f"/Users/linzhiji/Downloads/{processId}"
video_path=f"{videoDir}/{processId}-mute.mp4"
splitVideoDir=f"{videoDir}/split/"
os.makedirs(splitVideoDir, exist_ok=True)
splitVideoFastByPath(video_path, splitVideoDir)

subVideoList=getVideoPathsFromDir(splitVideoDir)





