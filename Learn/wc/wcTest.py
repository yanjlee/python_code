import wordcloud
import jieba
# from scipy.misc import imread
# mask = imread()

f = open('zmgj.txt','r',encoding='utf-8')
t =f.read()
f.close()
ls = jieba.lcut(t)
txt = " ".join(ls)
# print(txt)
font = r'C:\Windows\Fonts\simsun.ttc'
w = wordcloud.WordCloud(collocations=False, font_path=font, width=900, height=900, margin=2,background_color="white")
# w = wordcloud. WordCloud(width=1000, height=700, background_color="white")#,mask = mask)
w.generate(txt)
w.to_file('test.png')