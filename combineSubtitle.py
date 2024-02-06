import subprocess



def combinSubtitle(outPutMp4, subtitleDstPath, outPutSubtitleMp4):
    # ffcommand=f"ffmpeg -i {outPutMp4} -vf subtitles={subtitleDstPath}:force_style='FontName=simsun' {outPutSubtitleMp4}"
    ffcommand=f"ffmpeg -y -i {outPutMp4} -vf subtitles=\"{subtitleDstPath}:force_style='Alignment=2,BorderStyle=3,Outline=1,Shadow=0,FontSize=12'\" {outPutSubtitleMp4}"
    # api_logger.info(f"FFMPEG 合成字幕命令：{ffcommand}")
    result = subprocess.check_output(ffcommand, shell=True)

# ffmpeg -y -i english.mp4 -vf "subtitles=english.srt:force_style='Alignment=1,OutlineColour=&H100000000,BorderStyle=3,Outline=1,Shadow=0,FontName=Arial,FontSize=24,MarginL=40,MarginR=140,MarginV=10'"  -c:v libx264 -crf 23 -c:a copy output_video.mp4
