
from moviepy.editor import *
from utils.util import Util

# videoSrcPath = "./sample/simple5.mp4"
# clip = VideoFileClip(videoSrcPath)
# print("done")

frameOutDir="./out/simple5/cartoon/"
outVideoPath="./out/simple5/simple5-cartoon.mp4"
kFixedFps=24
result_frames = Util.get_image_paths_from_folder(frameOutDir)

result_frames.sort()
final_vid = Util.create_video(result_frames, kFixedFps, outVideoPath)
# api_logger.info(f"视频保存到 {outVideoPath}")