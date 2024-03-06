from combineSubtitle import *
import srt
import pysrt

# srcFilePath = "/Users/linzhiji/Downloads/7TWKKwwF30/7TWKKwwF30-en.srt"
# dstFilePath = "/Users/linzhiji/Downloads/7TWKKwwF30/7TWKKwwF30-en-recompse.srt"

srcFilePath = "./sample/simple5-cn.srt"

# recomposeEnSrt(srcSrtFilePath=srcFilePath, outSrtFilePath=dstFilePath)
subList = []
with open(srcFilePath, 'r') as srcFile:
    content = srcFile.read()
    subs = srt.parse(content)
    
    for sub in subs:
        subList.append(sub)


# print(subList)

subs = pysrt.open(srcFilePath)
print(len(subs))
first_sub = subs[0]
print(first_sub)