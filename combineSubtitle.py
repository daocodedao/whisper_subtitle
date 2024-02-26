import subprocess
from utils.logger_settings import api_logger
import os
import cv2


def check_video_verticle(filepath):
    # 打开视频文件
    video = cv2.VideoCapture(filepath)
    
    if not video.isOpened():
        api_logger.error(f"无法打开视频文件{filepath}")
        return True
        
    # 获取第一帧图像
    ret, frame = video.read()
    
    if not ret:
        api_logger.error(f"读取视频失败{filepath}")
        return True
    
    # 获取图像的高度和宽度
    height, width, _ = frame.shape
    
    # 根据比例确定视频的显示模式（横向/纵向）
    aspect_ratio = float(width / height)
    
    # 关闭视频流
    video.release()

    if aspect_ratio < 1.0:
        # display_mode = "横屏"
        api_logger.info(f"视频文件{filepath}是竖屏视频")
        return True
    else:
        api_logger.info(f"视频文件{filepath}是横屏视频")
        return False

    
 
    
    # return display_mode


def combinSubtitle(outPutMp4, subtitleDstPath, outPutSubtitleMp4):
    # ffcommand=f"ffmpeg -i {outPutMp4} -vf subtitles={subtitleDstPath}:force_style='FontName=simsun' {outPutSubtitleMp4}"
    if os.path.isfile(outPutSubtitleMp4):
        os.remove(outPutSubtitleMp4)
    # ffmpeg -i source_video_path.mp4 -vf "subtitles=srt_source.srt:force_style='OutlineColour=&H80000000,BorderStyle=4,BackColour=&H80000000,Outline=0,Shadow=0,MarginV=25,Fontname=Arial,Fontsize=10,Alignment=2'" video_destination.mp4

    # 竖屏的视频，字幕距离底部更高一些
    marginBottom = 45
    fontSize = 8
    # 横屏
    if not check_video_verticle(outPutMp4):
        marginBottom = 15
        fontSize = 12                     

    ffcommand=f"ffmpeg -y -i {outPutMp4} -vf subtitles=\"{subtitleDstPath}:force_style='FontName=ubuntu,Alignment=2,Outline=1,Shadow=0,FontSize={fontSize},MarginV={marginBottom}'\" {outPutSubtitleMp4}"
    api_logger.info(f"FFMPEG 合成字幕命令：")
    api_logger.info(ffcommand)
    result = subprocess.check_output(ffcommand, shell=True)

# ffmpeg -y -i english.mp4 -vf "subtitles=english.srt:force_style='Alignment=1,OutlineColour=&H100000000,BorderStyle=3,Outline=1,Shadow=0,FontName=Arial,FontSize=24,MarginL=40,MarginR=140,MarginV=10'"  -c:v libx264 -crf 23 -c:a copy output_video.mp4
