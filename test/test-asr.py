
import srt,sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import utilAsr

videoDir = "/Users/linzhiji/Downloads/longvideo"
processId = "8BxjAbLWfrM"
combineMp3Path = f"{videoDir}/{processId}/{processId}.mp3"
outSrtAsrCnPath = os.path.join(videoDir, f"{processId}-asr-cn.srt")


utilAsr.start_zh_asr_to_srt(combineMp3Path, outSrtAsrCnPath)

print("done")