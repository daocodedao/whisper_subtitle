

import configparser
import os
import platform
import getpass
import socket
from enum import Enum
from datetime import datetime


configPath=f"./config/config-{socket.gethostname()}.ini"

class TaskType(Enum):
    Download = "Download"
    Split = "Split"
    Understand = "Understand"
    OriginalVideo = "OriginalVideo"
    SensitiveCheck = "SensitiveCheck"
    ChannelMonitor = "ChannelMonitor"

class TaskStartType(Enum):
    FromStartId  = "FromStartId"
    FromSpecificId  = "FromSpecificId"
    FromCategory  = "FromCategory"

def needCreateStory():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = True
    if config.has_option("task", "needCreateStory"):
        configValue = config.get("task", "needCreateStory")
        configValue = bool(int(configValue))
    return configValue

def needDownloadVideo():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = True
    if config.has_option("task", "needDownloadVideo"):
        configValue = config.get("task", "needDownloadVideo")
        configValue = bool(int(configValue))
    return configValue

def needCheckSensitive():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = True
    if config.has_option("task", "needCheckSensitive"):
        configValue = config.get("task", "needCheckSensitive")
        configValue = bool(int(configValue))
    return configValue

def needMonitorChannel():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needMonitorChannel"):
        configValue = config.get("task", "needMonitorChannel")
        configValue = bool(int(configValue))
    return configValue

def needUpdateVectorDb():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needUpdateVectorDb"):
        configValue = config.get("task", "needUpdateVectorDb")
        configValue = bool(int(configValue))
    return configValue



def needSplitVideo():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = True
    if config.has_option("task", "needSplitVideo"):
        configValue = config.get("task", "needSplitVideo")
        configValue = bool(int(configValue))
    return configValue

def needUnderstandVideo():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = True
    if config.has_option("task", "needUnderstandVideo"):
        configValue = config.get("task", "needUnderstandVideo")
        configValue = bool(int(configValue))
    
    return configValue

def needStatsDaily():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needStatsDaily"):
        configValue = config.get("task", "needStatsDaily")
        configValue = bool(int(configValue))
    
    return configValue

def needProcessPushVideo():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needProcessPushVideo"):
        configValue = config.get("task", "needProcessPushVideo")
        configValue = bool(int(configValue))
    
    return configValue

def needDownloadFromStartId():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needDownloadFromStartId"):
        configValue = config.get("task", "needDownloadFromStartId")
        configValue = bool(int(configValue))
    
    return configValue

def needTtsFromShortVideo():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needTtsFromShortVideo"):
        configValue = config.get("task", "needTtsFromShortVideo")
        configValue = bool(int(configValue))
    
    return configValue

def needSplitFromStartId():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needSplitFromStartId"):
        configValue = config.get("task", "needSplitFromStartId")
        configValue = bool(int(configValue))
    
    return configValue

def needTransLateVideo():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = False
    if config.has_option("task", "needTransLateVideo"):
        configValue = config.get("task", "needTransLateVideo")
        configValue = bool(int(configValue))
    
    return configValue
 

def getMachineIdx():
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(configPath)
    configValue = 0
    if config.has_option("task", "machineIdx"):
        configValue = config.get("task", "machineIdx")
        configValue = int(configValue)
    
    return configValue

def getUnderstandStartId():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = 1
    if config.has_option("understand", "startId"):
        configValue = config.get("understand", "startId")
        configValue = int(configValue)
    
    return configValue

def getTtsStartId():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = 1
    if config.has_option("tts", "startId"):
        configValue = config.get("tts", "startId")
        configValue = int(configValue)
    
    return configValue

def getDownloadStartId():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = 1
    if config.has_option("download", "startId"):
        configValue = config.get("download", "startId")
        configValue = int(configValue)
        
    return configValue

def getSplitStartId():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = 1
    if config.has_option("split", "startId"):
        configValue = config.get("split", "startId")
        configValue = int(configValue)
        
    return configValue

def getStoryVideoStartId():
    config = configparser.ConfigParser()
    config.read(configPath)
    configValue = 1
    if config.has_option("story", "storyVideoStartId"):
        configValue = config.get("story", "storyVideoStartId")
        configValue = int(configValue)
        
    return configValue

gVideoPath = None
def getDataRootDir():
    global gVideoPath
    if not gVideoPath:
        config = configparser.ConfigParser()
        config.read(configPath)
        gVideoPath = "/data3/work/"
        if config.has_option("path", "dataWorkRoot"):
            gVideoPath = config.get("path", "dataWorkRoot")
            
        if platform.system() == "Mac" or platform.system() == "Darwin":
            gVideoPath = f"/Users/{getpass.getuser()}/Downloads/longvideos/"
    
        os.makedirs(gVideoPath, exist_ok=True)
    return gVideoPath

def getLongVideoDir():
    rootDir = getDataRootDir()
    return os.path.join(rootDir, "longVideos/")

def getStoryVideoDir(processId):
    rootDir = getDataRootDir()
    retDir = os.path.join(rootDir, f"story/{processId}/")
    os.makedirs(retDir, exist_ok=True)
    return retDir

gVideoDescServer = None
def getVideoDescServer():
    global gVideoDescServer
    if not gVideoDescServer:
        config = configparser.ConfigParser()
        config.read(configPath)
        if config.has_option("server", "videoDescServer"):
            gVideoDescServer = config.get("server", "videoDescServer")
            
        else:
            gVideoDescServer = "http://39.105.194.16:6690"
    return gVideoDescServer

def getVideoDescAPI():
    serverUrl = getVideoDescServer()
    serverUrl = serverUrl + "/video/describe"
    return serverUrl     

def getVideoSearchAPI():
    serverUrl = getVideoDescServer()
    serverUrl = serverUrl + "/video/search"
    return serverUrl     


def getShorVideoTableLastUpdateTime():
    config = configparser.ConfigParser()
    config.read(configPath)
    if config.has_option("ShortVideoTable", "lastUpdateTime"):
        lastUpdateTimeStr = config.get("ShortVideoTable", "lastUpdateTime")
        last_update = datetime.fromisoformat(lastUpdateTimeStr)
    else:
        last_update = datetime(2023, 1, 1)
    return last_update

def updateShorVideoTableLastUpdateTime(updateTime:datetime):
    if not updateTime:
        return
    config = configparser.ConfigParser()
    date_str = updateTime.isoformat()
    config['ShortVideoTable'] = {'lastUpdateTime': date_str}
    # 写入到.ini文件
    with open(configPath, 'w') as configfile:
        config.write(configfile)

def getTranslateVideoDir(processId = None):
    rootDir = getDataRootDir()
    if processId:
        retDir = os.path.join(rootDir, f"translate/{processId}/")
    else:
        retDir = os.path.join(rootDir, f"translate/")
    os.makedirs(retDir, exist_ok=True)
    return retDir


# if __name__ == "__main__":
#     needCreateStory()
