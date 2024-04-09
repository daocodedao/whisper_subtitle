import srt,sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from combineSubtitle import *
from utils.util import Util
from utils.mediaUtil import MediaUtil


def deleteNoHumanParts(inVideoPath, outVideoPath, srcPath):
    noHumanParts = MediaUtil.getNoHumanParts(srcPath)
    cmd = MediaUtil.create_ffmpeg_cmd(noHumanParts, inVideoPath, outVideoPath)
    print(cmd)

    subprocess.call(cmd, shell=True)
    print("done")

processId = "ZG2UUyMxkX4"

if Util.isMac():
    videoDir = "/Users/linzhiji/Downloads/ZG2UUyMxkX4/"
else:
    videoDir = f"/data/work/translate/{processId}"


# videoDir = os.path.dirname(videoPath)

ttsDir = os.path.join(videoDir, "tts")
videoPath = os.path.join(videoDir, f"{processId}.mp4")
videoMutePath = os.path.join(videoDir, f"{processId}-mute.mp4")
videoCnPath = os.path.join(videoDir, f"{processId}-cn.mp4")
videoCnSubtitlePath = os.path.join(videoDir, f"{processId}-cn-subtitle.mp4")
videoCnSubtitleBgPath = os.path.join(videoDir, f"{processId}-cn-subtitle-bg.mp4")
videoCartoonPath = os.path.join(videoDir, f"{processId}-cartoon.mp4")
videoCutOutPath =  os.path.join(videoDir, f"{processId}-cut.mp4")


srcAudioPath = os.path.join(videoDir, f"{processId}.wav")
combineMp3Path = os.path.join(videoDir, f"{processId}.mp3")
combineMp3SpeedPath = os.path.join(videoDir, f"{processId}-speed.mp3")
audioInsPath = os.path.join(videoDir, f"{processId}-ins.wav")

outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtEnReComposePath = os.path.join(videoDir, f"{processId}-en-recompse.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
outSrtTtsCnPath = os.path.join(videoDir, f"{processId}-tts-cn.srt")
outSrtAsrCnPath = os.path.join(videoDir, f"{processId}-asr-cn.srt")



deleteNoHumanParts(videoCnPath, videoCutOutPath, outSrtTtsCnPath)


# deleteRange = [(40.12/1000, 46.583/1000), (51.312/1000, 53.229/1000), (128.055/1000, 130.536/1000)]
# cmd = create_ffmpeg_cmd(deleteRange, "foo.mp4", "out.mp4")
# print(cmd)