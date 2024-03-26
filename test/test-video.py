
from moviepy.editor import *
from utils.util import Util
from utils.mediaUtil import MediaUtil
import re
import moviepy.editor as mp
from utils.logger_settings import api_logger

# videoSrcPath = "./sample/simple5.mp4"
# clip = VideoFileClip(videoSrcPath)
# print("done")

def combineVideoFromDir():
    frameOutDir="/Users/linzhiji/Downloads/cartoon"
    # outDir = os.path.dirname(frameOutDir)
    outVideoPath=os.path.join(frameOutDir,"out.mp4")
    kFixedFps=24
    result_frames = MediaUtil.get_image_paths_from_folder(frameOutDir)

    # result_frames.sort()
    result_frames.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

    print(result_frames)
    final_vid = MediaUtil.create_video(result_frames, kFixedFps, outVideoPath)
    api_logger.info(f"视频保存到 {outVideoPath}")

combineVideoFromDir()

def resizeVideo():
    clip = mp.VideoFileClip("/Users/linzhiji/Downloads/cartoon/BiB9YykxoZw-cn-subtitle.mp4")
    width = clip.w
    height = clip.h
    kMaxWidthOrHeight = 540
    if width > height:
        if width > kMaxWidthOrHeight:
            clip_resized = clip.resize(width=kMaxWidthOrHeight)
    else:
        if height > kMaxWidthOrHeight:
            clip_resized = clip.resize(height=kMaxWidthOrHeight)

    clip_resized.write_videofile("/Users/linzhiji/Downloads/cartoon/movie_resized.mp4")