
import whisper
import json
from pathlib import Path
from typing import Iterator, TextIO
import srt,sys,os
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from combineSubtitle import *
from utilAsr import start_zh_asr_to_srt
from utils.logger_settings import api_logger
from utils.util import Util

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

def whisper_transcribe_cn(file="{}/audio.mp3".format(dir), download_root = "./models/"):
    '''transcribe audio to text using whisper'''
    api_logger.info(f"生成中文字幕：file={file}")
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    if torch.cuda.is_available():
        model = whisper.load_model("medium", download_root=download_root, device=device)
    else:
        model = whisper.load_model("base", download_root=download_root, device=device)
    init_prompt = "你好，需要生成中文字幕。"

    result = model.transcribe(file, fp16=False, language="Chinese", word_timestamps=True, initial_prompt=init_prompt)
    
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


processId = "ZG2UUyMxkX4"

if Util.isMac():
    videoDir = "/Users/linzhiji/Downloads/ZG2UUyMxkX4/"
else:
    videoDir = f"/data/work/translate/{processId}"

# videoDir = os.path.dirname(videoPath)

ttsDir = os.path.join(videoDir, "tts")
videoPath = os.path.join(videoDir, f"{processId}.mp4")
videoMutePath = os.path.join(videoDir, f"{processId}-mute.mp4")
videoCnPath = os.path.join(videoDir, f"{processId}-cn.mp4")
videoCnSubtitlePath = os.path.join(videoDir, f"{processId}-cn-subtitle.mp4")
videoCnSubtitleBgPath = os.path.join(videoDir, f"{processId}-cn-subtitle-bg.mp4")
videoCartoonPath = os.path.join(videoDir, f"{processId}-cartoon.mp4")

srcAudioPath = os.path.join(videoDir, f"{processId}.wav")
combineMp3Path = os.path.join(videoDir, f"{processId}.mp3")
combineMp3SpeedPath = os.path.join(videoDir, f"{processId}-speed.mp3")
audioInsPath = os.path.join(videoDir, f"{processId}-ins.wav")

outSrtEnPath = os.path.join(videoDir, f"{processId}-en.srt")
outSrtEnReComposePath = os.path.join(videoDir, f"{processId}-en-recompse.srt")
outSrtCnPath = os.path.join(videoDir, f"{processId}-cn.srt")
outSrtTtsCnPath = os.path.join(videoDir, f"{processId}-tts-cn.srt")
outSrtAsrCnPath = os.path.join(videoDir, f"{processId}-asr-cn.srt")


curVideoPath = videoCnPath
language="chinese"
result, json_object = whisper_transcribe_cn(curVideoPath)
whisper_result_to_srt(result, outPath=outSrtTtsCnPath, language=language)

# api_logger.info("根据音频生成中文字幕")
# start_zh_asr_to_srt(combineMp3Path, outSrtAsrCnPath)