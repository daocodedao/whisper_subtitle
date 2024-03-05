from funasr import AutoModel
# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
# model = AutoModel(model="paraformer-zh",  vad_model="fsmn-vad",  punc_model="ct-punc-c", 
#                   # spk_model="cam++", 
#                   )
model = AutoModel(model="fa-zh")

audioPath="./sample/simple5-combine.mp3"
text_file="./out/simple5-combine.txt"
# res = model.generate(input=audioPath, 
#                      batch_size_s=300, 
#                      hotword='魔搭')

res = model.generate(input=(audioPath, text_file), 
                     data_type=("sound", "text"))

print(res)