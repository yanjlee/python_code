import tushare as ts
from textrank4zh import TextRank4Sentence

ts_pro=ts.pro_api（）
def cctv_abstract（date）：

#从CCTV新闻联播当天的内容中抽取10个句子作为摘要
#：param date:str日期，如：20181222
#：return:str

news=ts_pro.cctv_news（date=date）

contents="".join（list（news['content']））
tr4s=TextRank4Sentence（）
tr4s.analyze（text=contents，lower=True，source='all_filters'）
abstract=[]
for item in tr4s.get_key_sentences（num=100）：if len（item.sentence）〈300：abstract.append（[item.index，item.sentence]）
abstract=sorted（abstract[：10]，key=lambda x:x[0]）
abstract=["（%i）%s。\n"%（i，x[1]）for i，x in enumerate（abstract，1）]
return"".join（abstract）