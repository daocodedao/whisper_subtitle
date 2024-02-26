from translate import Translator

translator= Translator(to_lang="zh")
translation = translator.translate("Force yourself to read in situations and settings when it's least convenient.")
print(translation)
# translate-cli -t zh "This is how many books an average CEO reads a year." -o