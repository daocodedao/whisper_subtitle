
from typing import Optional
from pydantic import BaseModel
import os
import cv2
from typing import List
import socket
from datetime import datetime

# import 路径修改
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.videoBase import VideoStatus
from taskConfig import getDataRootDir


class ShortVideo(BaseModel):
    id:int = None
    longVideoId:int = None
    # 时长
    duration:float = 0
    # 在原视频里的开始时间
    startTime:float = 0
    # 在原视频里的结束时间
    endTime:float = 0
    # 视频描述
    desc:Optional[str] = ""
    # 音频识别
    srcTts:Optional[str] = ""
    isTts:bool=False

    width:int = 0
    height:int = 0
    tags:str = None
    category:str = None

    # 横屏还是竖屏
    isHorizontal:bool=True
    # 处理中
    isProcessing:bool=False
    status:int = VideoStatus.Normal.value

    # 敏感词是否检测过
    isSensitiveChecked:bool = False
    # 是否审核过
    isReviewed:bool = False

    # 存储地址
    videoPath:str = None

    # updateTime:Optional[datetime] = datetime.now()
    machineName:Optional[str] = socket.gethostname()

    def getAbsVideoPath(self):
        if self.videoPath:
            return os.path.join(getDataRootDir(), self.videoPath)
        else:
            return None
        
    def updateVideoPath(self, videoPath):
        if not os.path.exists(videoPath):
            return 
        
        self.videoPath = videoPath
        # 觉得路径换成相对路径
        self.videoPath = self.videoPath.replace(getDataRootDir(), "")
        video = cv2.VideoCapture(videoPath)
        fps = video.get(cv2.CAP_PROP_FPS)
        totalNoFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.duration = totalNoFrames / fps

        self.width  = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if self.width > self.height:
            self.isHorizontal = True
        else:
            self.isHorizontal = False

class LongVideo(BaseModel):
    id:int = None
    
    # 横屏还是竖屏
    isHorizontal:bool = True
    isProcessing:bool = False
    width:int = 0
    height:int = 0
    # 视频时长
    duration:float = 0

    shortVideos:List[ShortVideo] = []
    # 视频描述
    desc:Optional[str] = ""
    # 视频名
    name:str = None
    # 第三方视频ID
    thirdVideoId:str = None
    # 视频原url
    srcUrl:str = ""
    category:str = None
    # 第三方url，比如豆瓣，imdb
    thirdUrl:Optional[str] = None
    
    # 视频作者url
    srcChannelUrl:str = None
    # 语言 "en, cn"
    language:str = "en"
    # 视频类型，目前暂时不知道怎么分类
    tags:Optional[str] = None
    # 上映，发布时间
    publishTime:Optional[str] = None
    status:int = VideoStatus.Normal.value
    cutHeader:float = 0
    cutTail:float = 0
    
    # 相对路径
    videoPath:str = None
    # 子视频所在的文件夹，相对路径
    subVideoDir:str = None

    machineName:Optional[str] = socket.gethostname()
    # updateTime:Optional[datetime] = datetime.now()

    def getAbsVideoPath(self):
        if self.videoPath:
            return os.path.join(getDataRootDir(), self.videoPath)
        else:
            return None

    def getAbsSubVideoDir(self):
        if self.subVideoDir:
            return os.path.join(getDataRootDir(), self.subVideoDir)
        else:
            return None

    def updateVideoPath(self, videoPath):
        if not videoPath or not os.path.exists(videoPath):
            self.duration = 0  
            self.width = 0
            self.videoPath = None
            self.subVideoDir = None
            return 

        self.machineName = socket.gethostname()
        self.completeVideoInfo(videoPath)
        
        # videoName = os.path.basename(videoPath)
        # videoDir = os.path.dirname(videoPath)
        # self.subVideoDir = os.path.join(videoDir, 'subVideos')
        # os.makedirs(self.subVideoDir, exist_ok=True)
        # outVideoPath = os.path.join(videoDir, videoName)
        # if not os.path.exists(outVideoPath):
            # shutil.copyfile(videoPath, outVideoPath)
        
        # 绝对路径变为相对路径
        self.videoPath = videoPath
        self.videoPath = self.videoPath.replace(getDataRootDir(), "")
        self.subVideoDir = f"longVideos/{self.thirdVideoId}/subVideos"

    def completeVideoInfo(self, videoPath):
        video = cv2.VideoCapture(videoPath)
        # self.duration = video.get(cv2.CAP_PROP_POS_MSEC)
        fps = video.get(cv2.CAP_PROP_FPS)
        totalNoFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.duration = totalNoFrames / fps

        self.width  = video.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        self.height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        if self.width > self.height:
            self.isHorizontal = True
        else:
            self.isHorizontal = False

    def updateInfoFromYtDlp(self, videoDic):
        self.desc = videoDic["description"]
        videoTagList = videoDic["tags"]
        if len(videoTagList) > 0:
            self.tags = ",".join(videoTagList)
        self.name = videoDic["title"]

        self.thirdVideoId = videoDic["id"]
        if "-" in self.thirdVideoId:
            self.thirdVideoId = self.thirdVideoId.replace("-", "")
        self.srcChannelUrl = videoDic["uploader_url"]
        videoCategoryList = videoDic["categories"]
        if len(videoCategoryList) > 0:
            self.category = videoCategoryList[0]
        videoAvailability = videoDic["availability"]
        if videoAvailability != "public":
            self.status = VideoStatus.Deleted.value

