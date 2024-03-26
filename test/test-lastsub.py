import srt
from utils.logger_settings import api_logger
from utils.util import Util
from utils.mediaUtil import MediaUtil
import datetime



def addCustomSrt(srcPath, videoPath):
    subList = []
    with open(srcPath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)
        if len(subList) == 0:
            return 
        
    totalSub = len(subList)
    lastSub = subList[totalSub - 1]
    lastEndTime = lastSub.end.total_seconds()
    videoDuration = MediaUtil.getMediaDuration(videoPath)


    if videoDuration - lastEndTime > 2:
        api_logger.info("可以添加自定义话术")

        addSub = srt.Subtitle(index=totalSub + 1, 
                                start=datetime.timedelta(seconds=lastSub.end.seconds, microseconds=lastSub.end.microseconds + 120*1000), 
                                end=datetime.timedelta(seconds=lastSub.end.seconds + 1, microseconds=lastSub.end.seconds + 2000*1000 - 120*1000), 
                                content='随手来个赞或关注吧', 
                                proprietary='')

        with open(srcPath, "a", encoding="utf-8") as outFile:
            print(
                f"\n"
                f"{addSub.index}\n"
                f"{Util.format_timestamp(addSub.start.total_seconds(), always_include_hours=True)} --> "
                f"{Util.format_timestamp(addSub.end.total_seconds(), always_include_hours=True)}\n"
                f"{addSub.content}",
                file=outFile,
                flush=True,)
        
    api_logger.info("done")


videoPath = "/Users/linzhiji/Downloads/eR4G4khR6r8/eR4G4khR6r8.mp4"
outSrtEnReComposePath = "/Users/linzhiji/Downloads/eR4G4khR6r8/eR4G4khR6r8-cn.srt"


addCustomSrt(videoPath=videoPath, srcPath=outSrtEnReComposePath)
