from funasr import AutoModel
# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
from utils.logger_settings import api_logger
from typing import Iterator, TextIO

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

def write_srt(transcript: Iterator[dict], file: TextIO, language:str):
    api_logger.info("write transcript to SRT file")
    for i, segment in enumerate(transcript, start=1):
        lineStr = segment['text'].strip().replace('-->', '->')
        api_logger.info(lineStr)
        # if language == 'zh':
        #     lineStr = split_cnsubtitle(lineStr)
        api_logger.info(lineStr)
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{lineStr}",
            file=file,
            flush=True,
        )



audioPath="./sample/simple5-combine.mp3"
text_file="./out/simple5-combine.txt"
srt_file="./out/simple5-combine.srt"
model = AutoModel(model="paraformer-zh",  
                  vad_model="fsmn-vad",  
                  punc_model="ct-punc-c", 
                  sentence_timestamp=True
                  # spk_model="cam++", 
                  )
res = model.generate(input=audioPath, 
                     batch_size_s=300, 
                     hotword='魔搭')

# model = AutoModel(model="fa-zh")
# res = model.generate(input=(audioPath, text_file), 
#                      data_type=("sound", "text"))

for item in res:
    print("item:")
    # print(item)
    with open(srt_file, "w", encoding="utf-8") as srt:
        write_srt(item["sentence_info"], srt)
    # for sent in item["sentence_info"]:
    #     print(sent)
    #     print("\n\n\n")


