
import os
import shutil
from scenedetect import open_video, SceneManager, split_video_ffmpeg
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

from utils.util import Util
from utils.logger_settings import api_logger


def getVideoPathsFromDir(fromDir):
    if os.path.exists(fromDir) == False:
        return []
    else:
        videoList = [os.path.join(fromDir, f) for f in os.listdir(fromDir) if f.endswith(".mp4")]
        videoList = sorted(videoList)    
        return videoList


def splitVideoFastByPath(video_path, subVideoDir, threshold=30.0):

    # if Util.isMac():
    #     video_path = "./tmp/3728.mp4"

    if not video_path or os.path.exists(video_path) == False:
        return []
    # Open our video, create a scene manager, and add a detector.
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    scene_list = scene_manager.get_scene_list()
    api_logger.info(f"分析出有 {len(scene_list)} 个片段")
    # subVideoDir = longVideo.getAbsSubVideoDir()
    api_logger.info(f"准备 ffmpeg 切割, 输出目录 {subVideoDir} ")
    
    shutil.rmtree(subVideoDir, ignore_errors=True)
    os.makedirs(subVideoDir, exist_ok=True)
    # glob.glob(os.path.join(subVideoDir, '*'))

    split_video_ffmpeg(video_path, 
                        scene_list, 
                        show_progress=True,
                        output_dir=subVideoDir)
    videoPathList = getVideoPathsFromDir(subVideoDir)
    api_logger.info(f"切割完成, 共有 {len(videoPathList)} 个片段")
    return videoPathList