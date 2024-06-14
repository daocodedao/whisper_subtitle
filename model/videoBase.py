

from enum import Enum

class VideoStatus(Enum):
    #0 初始化 10 已经下载 20 已经切割 30 已经理解 80 已删除 90 文件不存在
    Init = 0
    Normal = 10
    Splitted = 20
    Understanded = 30
    CreatedStory = 40
    CreatedFail = 50
    Published = 60
    Deleted = 80
    FileNotExist = 90
    Downloaded = 110
    TranslateSuccess = 120
    #检测到敏感词

    Sensitive = 130

# 首页 番剧 国创 音乐 舞蹈 游戏 知识 科技 运动 汽车 生活
# 美食 动物圈 鬼畜 时尚 娱乐 影视 纪录片 电影 电视剧 直播 课堂
# 地图 历史 建筑 半导体 通信 交通 重型设备

# Animated Documentaries, History, Architecture, Flux-cored arc welding, Maps, 
# Semiconductors, Live, Wireless, Gaming, Trains, Heavy equipment, Flights,
# Home improvement, Information, Nature, Pop Music, 
# class VideoTags(Enum):
