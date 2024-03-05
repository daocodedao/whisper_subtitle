from combineSubtitle import *
import srt


# srcFilePath = "/Users/linzhiji/Downloads/7TWKKwwF30/7TWKKwwF30-en.srt"
# dstFilePath = "/Users/linzhiji/Downloads/7TWKKwwF30/7TWKKwwF30-en-recompse.srt"

srcFilePath = "./sample/wbHUdEeVeDU-cn.srt"

# recomposeEnSrt(srcSrtFilePath=srcFilePath, outSrtFilePath=dstFilePath)
subList = []
with open(srcFilePath, 'r') as srcFile:
    content = srcFile.read()
    subs = srt.parse(content)
    
    for sub in subs:
        subList.append(sub)


print(subList)