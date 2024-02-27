import srt
# from translate import Translator
from utils.logger_settings import api_logger
import subprocess
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import os
from utils.util import Util
from pydub import AudioSegment
import librosa
from scipy.io import wavfile
import argparse
from utils.Tos import TosService
from utils.translateFB import *
from combineSubtitle import *
from whisper.utils import get_writer
from collections import Counter


def format_timestamp(seconds: float, always_include_hours: bool = False):
    '''format timestamp to SRT format'''
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def whisper_transcribe_en(file="{}/audio.mp3".format(dir)):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("base")
    result = model.transcribe(file, fp16=False, language="English")
    json_object = json.dumps(result, indent=4)
    return result, json_object


def whisper_result_to_srt(whisper_result, outPath="", language: str = "cn"):
    '''converts whisper result to SRT format'''
    if len(outPath) == 0:
        file_name = Path(videoPath).stem
        outPath = "{}.srt".format(file_name)
    with open(outPath, "w", encoding="utf-8") as srt:
        write_srt(whisper_result["segments"], file=srt, language=language)
    return


def write_srt(transcript: Iterator[dict], file: TextIO, language: str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}",
            file=file,
            flush=True,
        )


def speed_change(input_file, output_file, speedRate: float = 1.0):
    song, fs = librosa.load(input_file)
    song_2_times_faster = librosa.effects.time_stretch(song, rate=speedRate)
    wavfile.write(output_file, fs, song_2_times_faster)  # save the song

def get_substring(string, percentage):
    length = int(len(string) * percentage)
    return string[:length]

def get_from_substring(string, percentage):
    length = int(len(string) * percentage)
    return string[length:]

def translate_srt(outSrtCnPath, outSrtEnPath):
    # translator = Translator(to_lang="zh")
    # outPath='./sample/simple5-cn.srt'
    with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
        with open(outSrtEnPath, 'r') as srcFile:
            # 读取文件内容
            content = srcFile.read()
            subs = srt.parse(content)
            subList = []
            for sub in subs:
                subList.append(sub)

            curHandleLine = -1
            for index in range(0, len(subList)):
                if index == curHandleLine:
                    continue
                sub = subList[index]
                append_punctuations: str = "?.,"
                # 最后一个字符不是标点符号
                curLineContent = sub.content
                lastChar = curLineContent[len(curLineContent) - 1]

                # 结尾不是标点符号, 准备连续操作两行
                if len(curLineContent) > 0 and lastChar not in append_punctuations and index + 1 < len(subList):
                    curLineCharCount = Counter(curLineContent)
                    nextLineContent = subList[index + 1].content
                    nextLineCharCount = Counter(nextLineContent)
                    waitTran = curLineContent + " " + nextLineContent
                    translation = translate_en_to_zh(waitTran)
                    api_logger.info(waitTran)
                    api_logger.info(translation)

                    # 准备写2行
                    # 第一行
                    line1Per = curLineCharCount.total()/(curLineCharCount.total()+nextLineCharCount.total())
                    translationLine1 = get_substring(translation, line1Per)
                    api_logger.info(sub.content)
                    api_logger.info(translationLine1)
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translationLine1}",
                        file=outFile,
                        flush=True,
                    )

                    index = index + 1
                    curHandleLine = index
                    sub = subList[index]
                    translationLine1 = get_from_substring(translation, line1Per)
                    api_logger.info(sub.content)
                    api_logger.info(translationLine1)
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translationLine1}",
                        file=outFile,
                        flush=True,
                    )
                            
                else:
                    # index = index + 1
                    translation = translate_en_to_zh(sub.content)
                    api_logger.info(sub.content)
                    api_logger.info(translation)
                    # api_logger.info(f"start second:{sub.start.total_seconds()} end:{sub.end.total_seconds()}")
                    print(
                        f"{sub.index}\n"
                        f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{translation}",
                        file=outFile,
                        flush=True,
                    )



def add_cn_tts(outSrtCnPath, videoMutePath, videoDir, processId):

    ttsDir = os.path.join(videoDir, "tts")
    combine_mp3_path = os.path.join(videoDir, f"{processId}.mp3")
    combine_mp3_speed_path = os.path.join(videoDir, f"{processId}-speed.mp3")

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
        for sub in subs:
            subList.append(sub)

    # print(len(subList))
    # index = 0
    combined = None
    totalSrtDuraton = 0
    totalGenDuration = 0
    for audioFile in wav_files:
        file_name_without_ext = os.path.splitext(
            os.path.basename(audioFile))[0]
        index = int(file_name_without_ext) - 1
        if index >= len(subList):
            continue

        audioFilePath = os.path.join(ttsDir, audioFile)
        curAudioFileDuration = Util.getMediaDuration(audioFilePath)
        sub = subList[index]
        timeDiff = sub.end.total_seconds() - sub.start.total_seconds()
        api_logger.info(f"中文音频时长: {curAudioFileDuration} srt时长:{timeDiff}  srt时长-中文音频:{timeDiff-curAudioFileDuration}")

        # 判断是否需要加入静音
        api_logger.info(f"当前字幕开始时间: {sub.start.total_seconds()} 已经合并的音频时长:{totalGenDuration}")
        if sub.start.total_seconds() > totalGenDuration:
            silence_duration = (
                sub.start.total_seconds() - totalGenDuration)*1000
            api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
            second_of_silence = AudioSegment.silent(duration=silence_duration)
            combined = combined + second_of_silence
            curAudioFileDuration = curAudioFileDuration + silence_duration/1000


        totalSrtDuraton = totalSrtDuraton + timeDiff
        totalGenDuration = totalGenDuration + curAudioFileDuration
        sound = AudioSegment.from_file(audioFilePath, format="wav")

        if combined is None:
            combined = sound
        else:
            combined = combined + sound

    file_handle = combined.export(combine_mp3_path, format="mp3")

    
    combine_mp3_duration = Util.getMediaDuration(combine_mp3_path)
    video_duration = Util.getMediaDuration(videoMutePath)
    api_logger.info(f"判断是否需要变速, combine_mp3_duration={combine_mp3_duration} video_duration={video_duration}")
    if combine_mp3_duration > video_duration:
        api_logger.info(f"视频需要变速, {combine_mp3_duration/video_duration}")
        speed_change(combine_mp3_path, combine_mp3_speed_path,
                     combine_mp3_duration/video_duration)
        combine_mp3_path = combine_mp3_speed_path

    cmd = f'ffmpeg -y -i {videoMutePath} -i {combine_mp3_path} -c:v copy -c:a aac {videoCnPath}'
    subprocess.call(cmd, shell=True)
    api_logger.info(f'完成任务: {videoCnPath}')

api_logger.info("准备开始")

program = argparse.ArgumentParser(
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
program.add_argument('-v', '--video', help='videoPath',
                     dest='videoPath', type=str, default='')
program.add_argument('-i', '--processId', help='process Id',
                     dest='processId', type=str, default='')
args = program.parse_args()


videoPath = args.videoPath
processId = args.processId

api_logger.info(f"videoPath: {videoPath} processId:{processId}")

language = "en"
videoDir = os.path.dirname(videoPath)
ttsDir = os.path.join(videoDir, "tts")
videoMutePath = os.path.join(videoDir, f"{processId}-mute.mp4")
videoCnPath = os.path.join(videoDir, f"{processId}-cn.mp4")
videoCnSubtitlePath = os.path.join(videoDir, f"{processId}-cn-subtitle.mp4")
outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")


api_logger.info("1---------视频生成英文SRT")
result, json_object = whisper_transcribe_en(videoPath)
whisper_result_to_srt(result, outPath=outSrtEnPath, language=language)

api_logger.info("2---------翻译中文SRT")
try:
    translate_srt(outSrtCnPath, outSrtEnPath)
except Exception as e:
    api_logger.error(f"翻译失败：{e}")
    exit(1)

api_logger.info("3---------中文SRT转TTS")
command = f"/data/work/GPT-SoVITS/start-gen-voice-local.sh -l 'zh'  -r 'lida' -s '{outSrtCnPath}' "
api_logger.info(f"命令：")
api_logger.info(command)
result = subprocess.check_output(command, shell=True)


api_logger.info("4---------原视频静音")
curVideoPath = videoPath
command = f"ffmpeg -y -i '{curVideoPath}' -c copy -an {videoMutePath}"
api_logger.info(f"命令：")
api_logger.info(command)
result = subprocess.check_output(command, shell=True)


api_logger.info("5---------视频加上中文TTS")
curVideoPath = videoMutePath
add_cn_tts(outSrtCnPath, curVideoPath, videoDir, processId)



api_logger.info("6---------视频加上中文字幕")
curVideoPath = videoCnPath
combinSubtitle(curVideoPath, outSrtCnPath, videoCnSubtitlePath)


api_logger.info("7---------上传到腾讯云")
curVideoPath = videoCnSubtitlePath
bucketName = "magicphoto-1315251136"
resultUrlPre = f"translate/video/{processId}/"
videoCnName=os.path.basename(curVideoPath)
reusultUrl = f"{resultUrlPre}{videoCnName}"
if os.path.exists(curVideoPath):
    api_logger.info(f"上传视频到OSS，curVideoPath:{curVideoPath}, task.key:{reusultUrl}, task.bucketName:{bucketName}")
    TosService.upload_file(curVideoPath, reusultUrl, bucketName)
    KCDNPlayUrl="http://magicphoto.cdn.yuebanjyapp.com/"
    playUrl = f"{KCDNPlayUrl}{reusultUrl}"
    api_logger.info(f"播放地址= {playUrl}")

    # 打开文件并写入
    dataFilePath = f"/data/work/translate/{processId}/output.txt"
    os.makedirs(os.path.dirname(dataFilePath), exist_ok=True)
    api_logger.info(f"url 列表写入文件: {dataFilePath}")
    with open(dataFilePath, "w") as file:
        file.write(playUrl + "\n")
else:
    api_logger.error(f"上传文件失败")
    exit(1)



exit(0)