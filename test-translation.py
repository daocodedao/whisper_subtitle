from translate import Translator

translator= Translator(to_lang="zh")
translation = translator.translate("This is how many books an average CEO reads a year.")
print(translation)
# translate-cli -t zh "This is how many books an average CEO reads a year." -o