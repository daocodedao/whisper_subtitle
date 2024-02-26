
from whisper.utils import get_writer
from utils.logger_settings import api_logger
import whisper
import json


def whisper_transcribe_en(file="{}/audio.mp3".format(dir)):
    '''transcribe audio to text using whisper'''
    model = whisper.load_model("base")
    result = model.transcribe(file, fp16=False, language="English")
    json_object = json.dumps(result, indent=4)
    return result, json_object

videoPath="./sample/simple5.mp4"
api_logger.info("1---------视频生成英文SRT")
result, json_object = whisper_transcribe_en(videoPath)
# whisper_result_to_srt(result, outPath=outSrtEnPath, language=language)

output_directory = "./sample/out"
# Save as an SRT file
srt_writer = get_writer("srt", output_directory)
srt_writer(result, videoPath)
