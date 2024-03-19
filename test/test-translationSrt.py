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
from utils.util import Util

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
            # print(f"start second:{sub.start.total_seconds()} end:{sub.end.total_seconds()}")
            print(
                f"{sub.index}\n"
                f"{Util.format_timestamp(sub.start.total_seconds(), always_include_hours=True)} --> "
                f"{Util.format_timestamp(sub.end.total_seconds(), always_include_hours=True)}\n"
                f"{translation}",
                file=outFile,
                flush=True,
            )
