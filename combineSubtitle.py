import subprocess
from utils.logger_settings import api_logger
import os

def combinSubtitle(outPutMp4, subtitleDstPath, outPutSubtitleMp4):
    # ffcommand=f"ffmpeg -i {outPutMp4} -vf subtitles={subtitleDstPath}:force_style='FontName=simsun' {outPutSubtitleMp4}"
    if os.path.isfile(outPutSubtitleMp4):
        os.remove(outPutSubtitleMp4)
    # ffmpeg -i source_video_path.mp4 -vf "subtitles=srt_source.srt:force_style='OutlineColour=&H80000000,BorderStyle=4,BackColour=&H80000000,Outline=0,Shadow=0,MarginV=25,Fontname=Arial,Fontsize=10,Alignment=2'" video_destination.mp4
# 
    ffcommand=f"ffmpeg -y -i {outPutMp4} -vf subtitles=\"{subtitleDstPath}:force_style='FontName=ubuntu,Alignment=2,Outline=1,Shadow=0,FontSize=8,MarginV=25'\" {outPutSubtitleMp4}"
    api_logger.info(f"FFMPEG 合成字幕命令：")
    api_logger.info(ffcommand)
    result = subprocess.check_output(ffcommand, shell=True)

# ffmpeg -y -i english.mp4 -vf "subtitles=english.srt:force_style='Alignment=1,OutlineColour=&H100000000,BorderStyle=3,Outline=1,Shadow=0,FontName=Arial,FontSize=24,MarginL=40,MarginR=140,MarginV=10'"  -c:v libx264 -crf 23 -c:a copy output_video.mp4
