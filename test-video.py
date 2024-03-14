
from moviepy.editor import *
from utils.util import Util
import re

# def sort_human(l):
#     convert = lambda text: float(text) if text.isdigit() else text
#     alphanum = lambda key: [convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
#     l.sort(key=alphanum)
#     return l

# def atoi(text):
#     return int(text) if text.isdigit() else text

# def natural_keys(text):
#     '''
#     alist.sort(key=natural_keys) sorts in human order
#     http://nedbatchelder.com/blog/200712/human_sorting.html
#     (See Toothy's implementation in the comments)
#     '''
#     return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# videoSrcPath = "./sample/simple5.mp4"
# clip = VideoFileClip(videoSrcPath)
# print("done")

frameOutDir="./out/simple5/cartoon/"
outVideoPath="./out/simple5/simple5-cartoon.mp4"
kFixedFps=24
result_frames = Util.get_image_paths_from_folder(frameOutDir)

# result_frames.sort()
result_frames.sort()

# result_frames = sort_human(result_frames)
print(result_frames)
final_vid = Util.create_video(result_frames, kFixedFps, outVideoPath)
# api_logger.info(f"视频保存到 {outVideoPath}")