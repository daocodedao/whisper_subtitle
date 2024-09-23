from pydub import AudioSegment
from utils.logger_settings import api_logger



silence_duration=6000.0
api_logger.info(f"需要加入静音音频， 时长：{silence_duration}毫秒")
second_of_silence = AudioSegment.silent(duration=silence_duration)