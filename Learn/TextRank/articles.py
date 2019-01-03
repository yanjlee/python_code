# codi#-*- encoding:utf-8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup as bs
from urllib import request as rq
from urllib.parse import quote
import string
import re
from textrank4zh import TextRank4Keyword, TextRank4Sentence

def review_list(number):
    # url = 'https://movie.douban.com/subject_search?search_text=\'' + '一袋弹子' + '&cat=1002'
    url = 'https://movie.douban.com/subject/'+ str(number) +'/reviews'
    url = quote(url, safe=string.printable)

    def filter(tag):
        return (tag.name == "a" and tag.has_attr("href") and tag["href"].startswith("https://movie.douban.com/review/"))

    response = rq.urlopen(url, timeout=20)
    result = response.read().decode('utf-8','ignore')#.replace(u'\xa9', u'')
    soup = bs(result,'lxml')
    tags = soup.find_all(filter)
    r_list = []
    for tag in tags:
        r_id = re.findall('[0-9]{7}', tag['href'])
        if len(r_id) != 0:
            r_list.append(r_id[0])
    r_list = list(set(r_list))
    return(r_list)

def texts(number):
    r_list = review_list(number)
    txt = ''
    for review in r_list:
        url = 'https://movie.douban.com/review/'+ str(review) +'/'
        response = rq.urlopen(url, timeout=20)
        result = response.read().decode('utf-8','ignore')#.replace(u'\xa9', u'')
        soup = bs(result,'lxml')
        tags = soup.find_all('p')
        if len(tags) > 0:
            for i in range(0,len(tags)):
                if len(tags[i].text) > 100:
                    txt = txt + tags[i].text
    return(txt)


def keys(number):
    key_words = '---关键词：\n'
    key_phrases = '---关键短语：\n'
    key_sentences = '---摘要：\n'
    txt = texts(number)
    # text = codecs.open(str(number) + '.txt', 'a+', 'utf-8').read()
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=txt, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    print( '关键词：' )
    print(tr4w.get_keywords(20, word_min_len=1))
    for item in tr4w.get_keywords(20, word_min_len=1):
        key_words = key_words + item.word + '\n'
        print(item.word, item.weight)
    print()
    print( '关键短语：' )
    for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
        key_phrases = key_phrases + phrase + '\n'
        print(phrase)
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=txt, lower=True, source = 'all_filters')
    print()
    print( '摘要：' )
    for item in tr4s.get_key_sentences(num=20):
        key_sentences = key_sentences + item.sentence + '\n'
        print(item.index, item.weight, item.sentence)
    text = open(str(number) + '.txt', 'a+', encoding='utf-8')
    text.write(key_words + '\n' + key_phrases + '\n' + key_sentences + '\n---全部文章：\n' + txt) # .encode(“gbk”, “ignore”)
    text.close()
    print('全部文章：')
    print(txt)

if __name__=="__main__":
    keys(26936217)
