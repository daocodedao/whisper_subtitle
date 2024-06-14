import srt
# from translate import Translator
from utils.logger_settings import api_logger
import subprocess
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import os
from pydub import AudioSegment
import librosa
from scipy.io import wavfile
import argparse
from utils.Tos import TosService
from utils.translateQwen import *
from combineSubtitle import *
import math
from utils.replaceKeyword import *
from utilAsr import start_zh_asr_to_srt
from utils.util import Util
from utils.mediaUtil import MediaUtil
import time
import sys
import datetime
import shutil
from utils import utilSensitive
from utils.notify import NotifyUtil

def whisper_transcribe_en(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    api_logger.info(f"生成字幕：file={file}")
    # device = torch.device('cuda' if torch.cuda.is_available() else 'mps') 

    model = whisper.load_model("medium", download_root=download_root, device='cuda')
    init_prompt = "Umm, let me think like, hmm... Okay, here's what I'm, like, thinking."
    # https://github.com/openai/whisper/discussions/625
    # init_prompt punctuator punctuation
    # init_prompt = "Umm, let me think like, like, thinking."
    result = model.transcribe(file, fp16=False, language="English", word_timestamps=True, initial_prompt=init_prompt)
    # result = model.transcribe(file, fp16=False, language="English", word_timestamps=True)
    
    json_object = json.dumps(result, indent=4)
    return result, json_object

def whisper_transcribe_cn(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    api_logger.info(f"生成中文字幕：file={file}")
    # device = torch.device('cuda' if torch.cuda.is_available() else 'mps') 

    model = whisper.load_model("medium", download_root=download_root, device='cuda')
    init_prompt = "你好，需要生成中文字幕。"

    result = model.transcribe(file, fp16=False, language="Chinese", word_timestamps=True, initial_prompt=init_prompt)
    
    json_object = json.dumps(result, indent=4)
    return result, json_object

def whisper_result_to_srt( whisper_result, outPath="", language: str = "cn"):
    
    '''converts whisper result to SRT format'''
    # if len(outPath) == 0:
    #     file_name = Path(videoPath).stem
    #     outPath = "{}.srt".format(file_name)
    with open(outPath, "w", encoding="utf-8") as srt:
        write_srt(whisper_result["segments"], file=srt, language=language)
    return

def write_srt(transcript: Iterator[dict], file: TextIO, language: str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(f"{i}\n"
            f"{Util.format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{Util.format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}")
        print(
            f"{i}\n"
            f"{Util.format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{Util.format_timestamp(segment['end'], always_include_hours=True)}\n"
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

def split_cnsubtitle(str1: str, maxlen=22) -> str:
    """
    拆分字幕中长度超过maxlen个字的中文字幕，超过后是均分两份，每份字符数 int(总字符数/份数+0.5)。

    默认Srt.CHINESE_SUBTITLE_LENGTH，22个字符

    最多拆为5行。

    如：字符共23个,按默认22字符拆分，则拆分为2行，然后均分2份，int(23/2+0.5)=12，第一行12个字符，第二行23-12=11个字符。

    如：字符共50个,按默认22字符拆分，则拆分为3行，然后均分int(50/3+0.5)=17，第一二行17个字符，第三行50-17-17=16个字符。

    以\n为折行。

    Arguments:
        str1 -- 待拆分的字符串

    Returns:
        拆分结果
    """
    if not str1:
        return str1
    ret = str1
    strlen = len(str1)
    splite_count = math.ceil(strlen / maxlen)
    splite_len = math.ceil(strlen / splite_count)
    if splite_count == 1:
            ret = str1
    elif splite_count == 2:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:]}"
    elif splite_count == 3:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:]}"
    elif splite_count == 4:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:]}"
    elif splite_count == 5:
            ret = f"{str1[0:splite_len]}\n{str1[splite_len:splite_len*2]}\n{str1[splite_len*2:splite_len*3]}\n{str1[splite_len*3:splite_len*4]}\n{str1[splite_len*4:]}"

    return ret

def translate_list_remote(preTrans:str, preTransEnSubList):
    # 尝试3次
    subZhList = []
    for i in range(0,3):
        api_logger.info(f"第{i}次翻译")
        subZhList = []
        try:
            zhContent = translate_srt_en_to_zh(preTrans)
            api_logger.info("分组翻译结果")
            api_logger.info(zhContent)

            zhSubs = srt.parse(zhContent)
            subZhList = list(zhSubs)
            
            # 分组翻译成功后，直接更新中文的时间戳，避免累积太多，视频最后都是静音
            isTranlateError = False
            if len(preTransEnSubList) >= len(subZhList) and len(subZhList) > 0:
                for index in range(0, len(subZhList)):
                    enSub = preTransEnSubList[index]
                    zhSub = subZhList[index]
                    if len(zhSub.proprietary) > 0:
                        api_logger.error(f"翻译错误，proprietary有内容: {zhSub.proprietary}")
                        isTranlateError = True
                        break

                    zhSub.start = enSub.start
                    zhSub.end = enSub.end

                if isTranlateError:
                    subZhList=[]
                    continue
                api_logger.info("分组翻译成功")
                break

        except Exception as e:
            subZhList=[]
            api_logger.error(f"翻译失败：{e}")

    # print(f"请求翻译次数{i}")
    if len(subZhList) == 0:
        api_logger.error("连续3次，字幕文件翻译成中文错误!")
        exit(1)
    
    return subZhList

def writeSublistToFile(zhAllSubList, outSrtCnPath):
    api_logger.info(f"写回文件：{outSrtCnPath}")
    with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
        for index in range(0, len(zhAllSubList)):
            zhSub = zhAllSubList[index]
            zhContent = zhSub.content
            zhContent = replaceSentenceWithKeyword(zhContent)

            print(
                f"{index + 1}\n"
                f"{Util.format_timestamp(zhSub.start.total_seconds(), always_include_hours=True)} --> "
                f"{Util.format_timestamp(zhSub.end.total_seconds(), always_include_hours=True)}\n"
                f"{zhContent}",
                file=outFile,
                flush=True,
            )

kMinMaxTranslateLineCount = 8
kMaxMaxTranslateLineCount = 10
def translate_srt(outSrtCnPath, inSrtFilePath, isVerticle = True):
    enAllSubList=[]
    with open(inSrtFilePath, 'r') as srcFile:
        content = srcFile.read()
        subs = srt.parse(content)
        enAllSubList = list(subs)

    zhAllSubList = []
    preTrans = ""
    enSubnList = []
    # 待翻译的英文字幕是否已经满了15个
    isFullNumberTranslate = False
    enPunctuations: str = "?.!"
    api_logger.info(f"字幕行数：{len(enAllSubList)}")
    transLateCount = 1
    for index in range(0, len(enAllSubList)):
        enSub = enAllSubList[index]
        curLineEnContent = enSub.content
        enSubnList.append(enSub)
        preTrans =  f"{preTrans}{enSub.index}\n{Util.format_timestamp(enSub.start.total_seconds(), always_include_hours=True)} --> {Util.format_timestamp(enSub.end.total_seconds(), always_include_hours=True)}\n{enSub.content}\n"
        
        if isFullNumberTranslate or (index + 1) % kMinMaxTranslateLineCount == 0 or index == len(enAllSubList)-1:
            isFullNumberTranslate = True

            if len(curLineEnContent) > 0:
                lastChar = curLineEnContent[len(curLineEnContent) - 1]
                # 结尾不是标点符号, 准备操作
                if lastChar not in enPunctuations and index + 1 < len(enAllSubList) and (index + 1) % kMinMaxTranslateLineCount != 0: 
                    api_logger.info(f"当前是{index}行。末尾不是.?, 继续取下一行。")
                    continue


            api_logger.info(f"准备第{transLateCount}组翻译")
            transLateCount = transLateCount + 1
            api_logger.info(preTrans)
            subZhList = translate_list_remote(preTrans, enSubnList)
            zhAllSubList = zhAllSubList + subZhList
            enSubnList=[]
            preTrans=""
            isFullNumberTranslate = False
            # 分组翻译重试3次
    
    writeSublistToFile(zhAllSubList, outSrtCnPath)
    
# 中文字幕根据屏幕宽度判断是否换行
def relayout_cn_tts(outSrtCnPath, isVerticle = True):
    maxCnSubtitleLen = 20
    if not isVerticle:
        maxCnSubtitleLen = 40
    subList = []
    with open(outSrtCnPath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)
    
    with open(outSrtCnPath, "w", encoding="utf-8") as outFile:
        for sub in subList:
            translation = sub.content
            translation = split_cnsubtitle(translation, maxCnSubtitleLen)
            print(
            f"{sub.index}\n"
            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
            f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
            f"{translation}",
            file=outFile,
            flush=True,)

def split_by_punctuations(instr, punctuations: list[str] = [",",".","?"]):
    line1Str = ""
    line2Str = instr

    if instr is None or len(instr) == 0:
        return line1Str, line2Str
    
    for punctuation in punctuations:
        if punctuation in instr :
            position = instr.find(punctuation)
            if position == len(instr) - 1:
                continue

            line1Str = instr[:position+1]
            line2Str = instr[position+2:]
            return line1Str, line2Str

    # 第二行没有找到标点符号，整体挪到上一行
    line1Str = instr
    line2Str = ""        
    return line1Str, line2Str

# 重新组合 英文字幕，这一行末尾不是英文标点符号，就到下一行去拿内容到这行
def recom_en_srt(inSrcFilePath, outSrcFilePath):
    # translator = Translator(to_lang="zh")
    # outPath='./sample/simple5-cn.srt'
    isModified = False
    with open(outSrcFilePath, "w", encoding="utf-8") as outFile:
        with open(inSrcFilePath, 'r') as srcFile:
            # 读取文件内容
            content = srcFile.read()
            subs = srt.parse(content)
            subList = list(subs)

            curHandleLine = -1
            lineIdx = 1
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
                    isModified = True
                    nextLineContent = subList[index + 1].content
                    line1, line2 = split_by_punctuations(nextLineContent)
                    if len(line1) > 0:
                        line1 = curLineContent + " " + line1
                    else:
                        line1 = curLineContent
                        isModified = False


                    if len(line2) > 0:
                        # 准备写2行
                        # 第一行
                        api_logger.info(lineIdx)
                        api_logger.info(line1)
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                            f"{line1}",
                            file=outFile,
                            flush=True,
                        )
                        lineIdx = lineIdx + 1

                        index = index + 1
                        sub = subList[index]
                        api_logger.info(lineIdx)
                        api_logger.info(line2)
                        curHandleLine = index
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                            f"{line2}",
                            file=outFile,
                            flush=True,
                        )
                        lineIdx = lineIdx + 1
                    else:
                        index = index + 1
                        curHandleLine = index
                        nextLineSub = subList[index]
                        curLineEndTime = nextLineSub.end.total_seconds()
                        api_logger.info(lineIdx)
                        api_logger.info(line1)
                        print(
                            f"{lineIdx}\n"
                            f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                            f"{Util.format_timestamp(curLineEndTime, always_include_hours=True)}\n"
                            f"{line1}",
                            file=outFile,
                            flush=True,
                        )
                            
                else:
                    api_logger.info(lineIdx)
                    api_logger.info(sub.content)
                    print(
                        f"{lineIdx}\n"
                        f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                        f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                        f"{sub.content}",
                        file=outFile,
                        flush=True,
                    )
                    lineIdx = lineIdx + 1
    
    return isModified

def loopHandleEn_srt(inSrcFilePath, outSrcFilePath):
    while(True):
        api_logger.info("整理英文SRT")
        isModified = recom_en_srt(inSrcFilePath, outSrcFilePath)
        if not isModified:
            break
        # 打开文件a并读取其内容
        with open(outSrcFilePath, 'r') as file_a:
            content_a = file_a.read()

        # 打开文件b并写入内容_a
        with open(inSrcFilePath, 'w') as file_b:
            file_b.write(content_a)

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
        # 字幕里有 sub.index ， 音频文件名字也对应的  index.wav
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

        # 字幕时间大于语音时间5秒，再加静音
        if sub.start.total_seconds() - totalGenDuration >= 5 and Util.lastCharIsCnClosePunctuations(sub.content):
            silence_duration = (sub.start.total_seconds() - totalGenDuration)*1000
            api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
            second_of_silence = AudioSegment.silent(duration=silence_duration)
            combined = combined + second_of_silence
            curAudioFileDuration = curAudioFileDuration + silence_duration/1000
        elif index == 0:
            if sub.start.total_seconds() > 0.5:
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
    # 音频时间 大于 视频时间，音频需要变速
    api_logger.info(f"判断是否需要变速, combine_mp3_duration={combine_mp3_duration} video_duration={video_duration}")
    if combine_mp3_duration > video_duration:
        api_logger.info(f"视频需要变速, {combine_mp3_duration/video_duration}")
        speed_change(combineMp3Path, combineMp3SpeedPath,
                     combine_mp3_duration/video_duration)
        combineMp3Path = combineMp3SpeedPath

    cmd = f'ffmpeg -y -i {videoMutePath} -i {combineMp3Path} -c:v copy -c:a aac {videoCnPath}'
    subprocess.call(cmd, shell=True)
    api_logger.info(f'完成任务: {videoCnPath}')

def addCustomSrt(srcPath, videoPath):
    subList = []
    with open(srcPath, 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        subList = list(subs)
        if len(subList) == 0:
            return 
        
    totalSub = len(subList)
    lastSub = subList[totalSub - 1]
    lastEndTime = lastSub.end.total_seconds()
    videoDuration = MediaUtil.getMediaDuration(videoPath)

    if videoDuration - lastEndTime > 2:
        api_logger.info("可以添加自定义话术")

        addSub = srt.Subtitle(index=totalSub + 1, 
                                start=datetime.timedelta(seconds=lastSub.end.seconds, microseconds=lastSub.end.microseconds + 120*1000), 
                                end=datetime.timedelta(seconds=lastSub.end.seconds + 1, microseconds=lastSub.end.seconds + 2000*1000 - 120*1000), 
                                content='随手来个赞或关注吧', 
                                proprietary='')

        with open(srcPath, "a", encoding="utf-8") as outFile:
            print(
                f"\n"
                f"{addSub.index}\n"
                f"{Util.format_timestamp(addSub.start.total_seconds(), always_include_hours=True)} --> "
                f"{Util.format_timestamp(addSub.end.total_seconds(), always_include_hours=True)}\n"
                f"{addSub.content}",
                file=outFile,
                flush=True,)
    else:
        api_logger.info("无需添加话术")

program = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
program.add_argument('-v', '--video', help='videoPath',
                     dest='videoPath', type=str, default='')
program.add_argument('-i', '--processId', help='process Id',
                     dest='processId', type=str, default='')
program.add_argument('-r', '--role', help='role',
                     dest='role', type=str, default='he')
program.add_argument('-b', '--isAddBgMusic', help='isAddBgMusic',
                     dest='isAddBgMusic', type=str, default='add')
program.add_argument('-t', '--needTranslate',
                     dest='needTranslate', type=str, default='translate')
program.add_argument('-c', '--needCartoon',
                     dest='needCartoon', type=str, default='noCartoon')
program.add_argument('-u', '--cutNoHumanVoiceThreshold',
                     dest='cutNoHumanVoiceThreshold', type=int, default=0)
args = program.parse_args()

api_logger.info(args)
videoPath = args.videoPath
processId = args.processId
isAddBgMusic = False
if args.isAddBgMusic == 'add':
    isAddBgMusic = True

isNeedTranslate = True
if args.needTranslate == 'noTranslate':
    isNeedTranslate = False

isNeedCartoon = False
if args.needCartoon == 'cartoon':
    isNeedCartoon = True

cutNoHumanVoiceThreshold = args.cutNoHumanVoiceThreshold

role = args.role

api_logger.info("准备开始")
api_logger.info(f"videoPath: {videoPath} processId:{processId} role={role} isAddBgMusic={isAddBgMusic} isNeedCartoon={isNeedCartoon} isNeedCartoon={isNeedCartoon}")

language = "en"
videoDir = os.path.dirname(videoPath)
ttsDir = os.path.join(videoDir, "tts")
nobgVideoPath = os.path.join(videoDir, f"{processId}-no-bgmusic.mp4")
videoMutePath = os.path.join(videoDir, f"{processId}-mute.mp4")
videoCnPath = os.path.join(videoDir, f"{processId}-cn.mp4")
videoCnSubtitlePath = os.path.join(videoDir, f"{processId}-cn-subtitle.mp4")
videoCnSubtitleBgPath = os.path.join(videoDir, f"{processId}-cn-subtitle-bg.mp4")
videoCartoonPath = os.path.join(videoDir, f"{processId}-cartoon.mp4")
videoCutPath = os.path.join(videoDir, f"{processId}-human-cut.mp4")

srcAudioPath = os.path.join(videoDir, f"{processId}.wav")
combineMp3Path = os.path.join(videoDir, f"{processId}.mp3")
# 变速后的音频地址
combineMp3SpeedPath = os.path.join(videoDir, f"{processId}-speed.mp3")
audioInsPath = os.path.join(videoDir, f"{processId}-ins.wav")

outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtEnReComposePath = os.path.join(videoDir, f"{processId}-en-recompse.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
outSrtTtsCnPath = os.path.join(videoDir, f"{processId}-tts-cn.srt")
outSrtAsrCnPath = os.path.join(videoDir, f"{processId}-asr-cn.srt")

isVerticle = False
if check_video_verticle(videoPath):
    isVerticle = True     

curVideoPath = videoPath

stepIndex = 1
api_logger.info(f"{stepIndex}---------视频卡通化")
if isNeedCartoon:    
    stepIndex = stepIndex + 1
    command = f"/data/work/aishowos/whisper_subtitle/start-cartoon.sh -v {curVideoPath} -i {processId} -a add"
    api_logger.info(command)
    result = subprocess.check_output(command, shell=True)
    Util.log_subprocess_output(result)
    if os.path.exists(videoCartoonPath):
        api_logger.info(f"视频卡通化成功 {videoCartoonPath}")
        curVideoPath = videoCartoonPath
    else:
        api_logger.error(f"视频卡通化失败")
        exit(1)

api_logger.info(f"{stepIndex}---------视频生成英文SRT")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    api_logger.info(f"从视频剥离音频文件 {srcAudioPath}")
    command = f"ffmpeg -y -i {curVideoPath} -vn -acodec pcm_f32le -ar 44100 -ac 2 {srcAudioPath}"
    api_logger.info(command)
    result = subprocess.check_output(command, shell=True)
    Util.log_subprocess_output(result)

    api_logger.info(f"生成字幕 {outSrtEnPath}")
    result, json_object = whisper_transcribe_en(curVideoPath)
    whisper_result_to_srt(result, outPath=outSrtEnPath, language=language)

    api_logger.info(f"敏感词检测 {outSrtEnPath}")
    isSensitive = utilSensitive.detectSensitiveFromSrt(outSrtEnPath)
    if isSensitive:
        notiMsg = "字幕包含敏感词"
        notiMsg = notiMsg + f"视频地址: {videoPath}\n"
        notiMsg = notiMsg + f"视频ID: {processId}\n"
        api_logger.info(notiMsg)
        NotifyUtil.notifyFeishu(notiMsg)
        exit(1)

    loopHandleEn_srt(inSrcFilePath=outSrtEnPath, outSrcFilePath=outSrtEnReComposePath)

api_logger.info(f"{stepIndex}---------英文SRT翻译中文SRT")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    try:
        # 字幕不要在这个函数里换行，会影响语音TTS
        api_logger.info("翻译中文字幕")
        translate_srt(outSrtCnPath, outSrtEnReComposePath, isVerticle)
        api_logger.info("检测字幕与视频时间戳，看看是否能添加话术")
        addCustomSrt(outSrtEnReComposePath, curVideoPath)
    except Exception as e:
        api_logger.error(f"翻译失败：{e}")
        exit(1)

api_logger.info(f"{stepIndex}---------中文SRT转TTS")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    try:
        command = f"/data/work/GPT-SoVITS/start-gen-voice-local.sh -l 'zh'  -r {role} -s '{outSrtCnPath}' "
        api_logger.info(f"命令：")
        api_logger.info(command)
        # api_logger.info(traceback.format_exc())
        result = subprocess.check_output(command, shell=True)
        Util.log_subprocess_output(result)
    except Exception as e:
        api_logger.error(f"中文SRT转TTS失败：{e}")
        exit(1)

api_logger.info(f"{stepIndex}---------原视频静音")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    try:
        command = f"ffmpeg -y -i '{curVideoPath}' -c copy -an {videoMutePath}"
        api_logger.info(f"命令：")
        api_logger.info(command)
        result = subprocess.check_output(command, shell=True)
        Util.log_subprocess_output(result)
        curVideoPath = videoMutePath
    except Exception as e:
        api_logger.error(f"原视频静音失败：{e}")
        exit(1)

api_logger.info(f"{stepIndex}---------视频加上中文TTS")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    try:
        add_cn_tts(outSrtCnPath, curVideoPath, videoDir, combineMp3Path, combineMp3SpeedPath)
        curVideoPath = videoCnPath
    except Exception as e:
        api_logger.error(f"视频加上中文TTS失败：{e}")
        exit(1)

api_logger.info(f"{stepIndex}---------视频加上中文字幕")
if isNeedTranslate:
    stepIndex = stepIndex + 1
    try:
        language="chinese"
        # result, json_object = whisper_transcribe_cn(curVideoPath)
        # whisper_result_to_srt(result, outPath=outSrtTtsCnPath, language=language)
        # relayout_cn_tts(outSrtTtsCnPath, isVerticle)
        # combinSubtitle(curVideoPath, outSrtTtsCnPath, videoCnSubtitlePath)
        
        # api_logger.info("根据音频生成中文字幕")
        # start_zh_asr_to_srt(combineMp3Path, outSrtAsrCnPath)
        # api_logger.info("中文字幕重新调整行数")
        # relayout_cn_tts(outSrtAsrCnPath, isVerticle)
        # api_logger.info("合并字幕到视频")
        # combinSubtitle(curVideoPath, outSrtAsrCnPath, videoCnSubtitlePath)

        api_logger.info("中文字幕重新调整行数")
        relayout_cn_tts(outSrtCnPath, isVerticle)
        combinSubtitle(curVideoPath, outSrtCnPath, videoCnSubtitlePath)
        curVideoPath = videoCnSubtitlePath
    except Exception as e:
        api_logger.error(f"视频加上中文字幕失败：{e}")
        exit(1)

api_logger.info(f"{stepIndex}---------剪切没有人声音且超过{cutNoHumanVoiceThreshold}秒的片段")
if isNeedTranslate and cutNoHumanVoiceThreshold > 0:
   
    stepIndex = stepIndex + 1

    api_logger.info(f"tts 根据视频生成中文字幕")
    language="chinese"
    result, json_object = whisper_transcribe_cn(curVideoPath)
    whisper_result_to_srt(result, outPath=outSrtTtsCnPath, language=language)

    noHumanParts = MediaUtil.getNoHumanParts(outSrtTtsCnPath, cutNoHumanVoiceThreshold)
    api_logger.info(f"获取需要没有人声的视频片段 {noHumanParts}")
    if len(noHumanParts) > 0:
        cmd = MediaUtil.create_ffmpeg_cmd(noHumanParts, curVideoPath, videoCutPath)
        api_logger.info(cmd)
        subprocess.call(cmd, shell=True)
        api_logger.info(f"剪切没有人声的视频片段")
        curVideoPath = videoCutPath
    else:
        api_logger.info(f"视频无需剪切")

if os.path.exists(curVideoPath):
    shutil.copyfile(curVideoPath, nobgVideoPath)

api_logger.info(f"{stepIndex}---------视频加上背景音乐")
if isNeedTranslate and isAddBgMusic:
    stepIndex = stepIndex + 1
    try:
        for tryIndex in range(0,5):
            try:
                api_logger.info(f"第{tryIndex + 1}获取背景音乐")
                command = f"/data/work/GPT-SoVITS/start-urv.sh -s {srcAudioPath} -i {processId} -n {audioInsPath}"
                api_logger.info(f"命令：")
                api_logger.info(command)
                result = subprocess.check_output(command, shell=True)
                Util.log_subprocess_output(result)
                if os.path.exists(audioInsPath):
                    api_logger.info(f'完成音频urv任务: {audioInsPath}')
                    break
            except Exception as e:
                api_logger.error(f"第{tryIndex + 1}次，获取背景音乐失败：{e} 休息2秒后重试")
                time.sleep(2)

        if os.path.exists(audioInsPath):
            api_logger.info(f"添加背景音乐 {curVideoPath}")
            command = f"ffmpeg -y -i {curVideoPath}  -i {audioInsPath} -c:v copy -filter_complex '[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.6[1a];[0a][1a]amerge[a]' -map 0:v -map '[a]' -ac 2 -shortest {videoCnSubtitleBgPath}"
            # command = f'ffmpeg -y -i {curVideoPath} -i {audioInsPath} -c copy -map 0:v:0 -map 1:a:0 {videoCnSubtitleBgPath}'
            api_logger.info(f"命令：")
            api_logger.info(command)
            result = subprocess.check_output(command, shell=True)
            Util.log_subprocess_output(result)
            api_logger.info(f'完成背景音乐合并任务: {videoCnSubtitleBgPath}')
            curVideoPath = videoCnSubtitleBgPath
        else:
            api_logger.error(f"背景音乐 {audioInsPath} 不存在")
    except Exception as e:
        api_logger.error(f"视频加上背景音乐失败：{e}")
            # exit(1)

api_logger.info(f"{stepIndex}---------上传到腾讯云")
stepIndex = stepIndex + 1
bucketName = "magicphoto-1315251136"
resultUrlPre = f"translate/video/{processId}/"
videoCnName=os.path.basename(curVideoPath)
reusultUrl = f"{resultUrlPre}{videoCnName}"
KCDNPlayUrl="http://magicphoto.cdn.yuebanjyapp.com/"
api_logger.info(f"上传视频 {curVideoPath}")
if os.path.exists(curVideoPath):
    api_logger.info(f"上传视频到OSS，curVideoPath:{curVideoPath}, task.key:{reusultUrl}, task.bucketName:{bucketName}")
    TosService.upload_file(curVideoPath, reusultUrl, bucketName)
    playUrl = f"{KCDNPlayUrl}{reusultUrl}"
    api_logger.info(f"播放地址= {playUrl}")

    # 打开文件并写入
    dataFilePath = f"{videoDir}/output.txt"
    os.makedirs(os.path.dirname(dataFilePath), exist_ok=True)
    api_logger.info(f"url 列表写入文件: {dataFilePath}")
    with open(dataFilePath, "w") as file:
        file.write(playUrl + "\n")
else:
    api_logger.error(f"上传文件失败, {curVideoPath}不存在")
    exit(1)

if os.path.exists(nobgVideoPath):
    videoCnName = os.path.basename(nobgVideoPath)
    reusultUrl = f"{resultUrlPre}{videoCnName}"

    api_logger.info(f"上传无背景音乐视频到OSS，curVideoPath:{nobgVideoPath}, task.key:{reusultUrl}, task.bucketName:{bucketName}")
    TosService.upload_file(nobgVideoPath, reusultUrl, bucketName)
    playUrl = f"{KCDNPlayUrl}{reusultUrl}"
    api_logger.info(f"无背景音乐播放地址= {playUrl}")

exit(0)