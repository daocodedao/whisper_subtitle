
import srt,sys
import subprocess
import os
from pydub import AudioSegment
import librosa
from scipy.io import wavfile

# import 路径修改
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.logger_settings import api_logger
from utils.util import Util
from utils.mediaUtil import MediaUtil

def speed_change(input_file, output_file, speedRate:float = 1.0):
    song, fs = librosa.load(input_file)
    song_2_times_faster = librosa.effects.time_stretch(song, rate=speedRate)
    wavfile.write(output_file, fs, song_2_times_faster) # save the song


def add_cn_tts(outSrtCnPath, videoMutePath, videoDir, combineMp3Path, combineMp3SpeedPath):

    ttsDir = os.path.join(videoDir, "tts")
    wav_files = [f for f in os.listdir(ttsDir) if f.endswith(".wav")]
    if(len(wav_files) == 0):
        api_logger.error("srt没有生成音频文件")
        exit(1)
    else:
        wav_files.sort(key=lambda x: '{0:0>8}'.format(x))
    
    subList = []
    with open(outSrtCnPath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)


    combined = None
    totalSrtDuraton = 0
    totalGenDuration = 0
    for audioFile in wav_files:
        file_name_without_ext = os.path.splitext(os.path.basename(audioFile))[0]
        index = int(file_name_without_ext) - 1
        if index >= len(subList):
            continue

        audioFilePath = os.path.join(ttsDir, audioFile)
        curAudioFileDuration = MediaUtil.getMediaDuration(audioFilePath)
        sub = subList[index]
        timeDiff = sub.end.total_seconds() - sub.start.total_seconds()
        api_logger.info(f"中文音频时长: {curAudioFileDuration} srt时长:{timeDiff}  srt时长-中文音频:{timeDiff-curAudioFileDuration}")

        # 判断是否需要加入静音
        api_logger.info(f"当前字幕开始时间: {sub.start.total_seconds()} 已经合并的音频时长:{totalGenDuration}")
        # if sub.start.total_seconds() > totalGenDuration:
        # 大于5秒再加静音
        if sub.start.total_seconds() - totalGenDuration >= 5 and Util.lastCharIsCnClosePunctuations(sub.content):
            silence_duration = (sub.start.total_seconds() - totalGenDuration)*1000
            api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
            second_of_silence = AudioSegment.silent(duration=silence_duration)
            combined = combined + second_of_silence
            curAudioFileDuration = curAudioFileDuration + silence_duration/1000
        elif index == 0:
            if sub.start.total_seconds() > 1:
                silence_duration = sub.start.total_seconds()*1000
                api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
                second_of_silence = AudioSegment.silent(duration=silence_duration)
                combined = second_of_silence
                curAudioFileDuration = curAudioFileDuration + silence_duration/1000


        totalSrtDuraton = totalSrtDuraton + timeDiff
        totalGenDuration = totalGenDuration + curAudioFileDuration
        sound = AudioSegment.from_file(audioFilePath, format="wav")

        if combined is None:
            combined = sound
        else:
            combined = combined + sound

    file_handle = combined.export(combineMp3Path, format="mp3")

    combine_mp3_duration = MediaUtil.getMediaDuration(combineMp3Path)
    video_duration = MediaUtil.getMediaDuration(videoMutePath)
    api_logger.info(f"判断是否需要变速, combine_mp3_duration={combine_mp3_duration} video_duration={video_duration}")
    if combine_mp3_duration > video_duration:
        api_logger.info(f"视频需要变速, {combine_mp3_duration/video_duration}")
        speed_change(combineMp3Path, combineMp3SpeedPath,
                     combine_mp3_duration/video_duration)
        combineMp3Path = combineMp3SpeedPath

    cmd = f'ffmpeg -y -i {videoMutePath} -i {combineMp3Path} -c:v copy -c:a aac {videoCnPath}'
    subprocess.call(cmd, shell=True)
    api_logger.info(f'完成任务: {videoCnPath}')


# videoDir = "/Users/linzhiji/Downloads/Abt7FwZwY/"
videoDir = "/Users/linzhiji/Downloads/ZG2UUyMxkX4/"
videoId = "ZG2UUyMxkX4"
videoPath=f"{videoDir}{videoId}.mp4"
videoMutePath=f"{videoDir}{videoId}-mute.mp4"
videoCnPath=f"{videoDir}{videoId}-cn.mp4"

outSrtEnPath=f"{videoDir}{videoId}-en.srt"
outSrtCnPath=f"{videoDir}{videoId}-cn.srt"
language="en"

combine_mp3_path = f"{videoDir}{videoId}-combine.mp3"
combine_mp3_speed_path = f"{videoDir}{videoId}-combine-speed.mp3"

combineMp3Path = os.path.join(videoDir, f"{videoId}.mp3")
combineMp3SpeedPath = os.path.join(videoDir, f"{videoId}-speed.mp3")



api_logger.info("5---------视频加上中文TTS")
try:
    curVideoPath = videoMutePath
    add_cn_tts(outSrtCnPath, curVideoPath, videoDir, combineMp3Path, combineMp3SpeedPath)
except Exception as e:
    api_logger.error(f"视频加上中文TTS失败：{e}")
    exit(1)

