import pkuseg


seg = pkuseg.pkuseg()           # 以默认配置加载模型
text = seg.cut('总的来说，<橙黄橘绿半 甜时> 是一本让人回味无穷，满足感官享受的美文集 。这不仅是一本书，更是一场心灵的盛 宴，一段历史与现在、人文与自然相交的记忆。')  # 进行分词
print(text)