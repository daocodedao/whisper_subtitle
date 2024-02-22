# import pysrt
# from translate import Translator

# subs = pysrt.open('./sample/simple5.srt')
# translator= Translator(to_lang="zh")

# for sub in subs:
#     print(sub.text)
#     translation = translator.translate(sub.text)
#     print(translation)
#     sub.text = translation

# subs.save('./sample/simple5-cn.srt', encoding='utf-8')

import srt
from translate import Translator

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


translator= Translator(to_lang="zh")
outPath='./sample/simple5-cn.srt'
with open(outPath, "w", encoding="utf-8") as outFile:
    with open('./sample/simple5.srt', 'r') as srcFile:
        # 读取文件内容
        content = srcFile.read()
        subs = srt.parse(content)
        for sub in subs:
            translation = translator.translate(sub.content)
            print(translation)
            print(f"start second:{sub.start.total_seconds()} end:{sub.end.total_seconds()}")
            print(
                f"{sub.index}\n"
                f"{format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                f"{format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                f"{translation}",
                file=outFile,
                flush=True,
            )
