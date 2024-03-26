
from utils.logger_settings import api_logger
import time,datetime,json,os
import random
import subprocess
import av
from PIL import Image
import cv2
from moviepy.editor import *

# 常用工具
class MediaUtil:

    def getRandomMp3FilePath(fromDir):
        mp3_files = [f for f in os.listdir(fromDir) if f.endswith(".mp3")]
        if not mp3_files:
            api_logger.info("No mp3 files found in the folder.")
            return ""
        else:
            random_mp3_file = random.choice(mp3_files)
            random_mp3_path = os.path.join(fromDir, random_mp3_file)
            api_logger.info(f"Random mp3 file: {random_mp3_path}")
            return random_mp3_path
    
    def getMediaDuration(filePath):
      try:
          cmd=f"ffprobe -i {filePath} -show_entries format=duration -v quiet -of csv=\"p=0\""
          result = subprocess.check_output(cmd, shell=True)
          durationFloat = float(result)
          return durationFloat
      except Exception as e:
          return 0

    def getRandomTransitionEffect():
      effects = ["DISSOLVE", "RADIAL", "CIRCLEOPEN", "CIRCLECLOSE", "PIXELIZE", "HLSLICE", 
              "HRSLICE", "VUSLICE", "VDSLICE", "HBLUR", "FADEGRAYS", "FADEBLACK", "FADEWHITE","RECTCROP",
              "CIRCLECROP", "WIPELEFT", "WIPERIGHT", "SLIDEDOWN", "SLIDEUP", "SLIDELEFT", "SLIDERIGHT"]
      return random.choice(effects).lower()
  
    def read_frames(video_path):
        container = av.open(video_path)

        video_stream = next(s for s in container.streams if s.type == "video")
        frames = []
        for packet in container.demux(video_stream):
            for frame in packet.decode():
                image = Image.frombytes(
                    "RGB",
                    (frame.width, frame.height),
                    frame.to_rgb().to_ndarray(),
                )
                frames.append(image)

        return frames
    
    def extract_video_to_frames(video_path, outDir):
        vidcap = cv2.VideoCapture(video_path)
        success,image = vidcap.read()
        count = 0
        framePaths = []
        while success:
            framePath = os.path.join(outDir, f"{count}.jpg")
            cv2.imwrite(framePath, image)     # save frame as JPEG file      
            framePaths.append(framePath)
            success,image = vidcap.read()
            # print('Read a new frame: ', success)
            count += 1

            return framePaths
        
    def get_image_paths_from_folder(folder_path):
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
        image_paths = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                for ext in image_extensions:
                    if file.endswith(ext):
                        image_path = os.path.join(root, file)
                        image_paths.append(image_path)

        image_paths.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        return image_paths
    
    def get_fps(video_path):
        container = av.open(video_path)
        video_stream = next(s for s in container.streams if s.type == "video")
        fps = video_stream.average_rate
        container.close()
        return fps
  
    def changeVideoFps(filePath, fps=30, outFilePath=None):
        # print(f"now fps = {int(get_fps(filePath))}")
        clip = VideoFileClip(filePath)
        if outFilePath is None:
            outFilePath = filePath

        clip.write_videofile(outFilePath, fps=fps)
        # print(f"now fps = {int(get_fps(outFilePath))}")


    def create_video(frames, fps, savePath):
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(savePath, fps=fps, verbose=False)
