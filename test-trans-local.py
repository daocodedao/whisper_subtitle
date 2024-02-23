from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import os

os.environ['HTTP_PROXY'] = '192.168.0.77:18808'
os.environ['HTTPS_PROXY'] = '192.168.0.77:18808'

article_cn = "This model is a fine-tuned checkpoint of mBART-large-50. mbart-large-50-many-to-many-mmt is fine-tuned for multilingual machine translation. "

model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")


tokenizer.src_lang = "en_XX"
encoded_zh = tokenizer(article_cn, return_tensors="pt")
generated_tokens = model.generate(**encoded_zh, forced_bos_token_id=tokenizer.lang_code_to_id["zh_CN"])
result = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
print(result)