from funasr import AutoModel
# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need


audioPath="./sample/simple5-combine.mp3"
text_file="./out/simple5-combine.txt"
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
    for sent in item["sentence_info"]:
        print(sent)
        print("\n\n\n")