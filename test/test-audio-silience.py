from pydub import AudioSegment
import srt,sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.logger_settings import api_logger



silence_duration=6000.0
api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
try:
    second_of_silence = AudioSegment.silent(duration=silence_duration)
except Exception as e:
    api_logger.error(f"原视频静音失败：{e}")