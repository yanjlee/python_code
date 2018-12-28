
# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import requests
from urllib import request
import random
from time import sleep, time
from http import cookiejar
import urllib
import urllib.request as urllib2
import http.cookiejar as cookielib
import json


import urllib
import http.cookiejar

filename = 'cookie.txt'
cookie = cookiejar.MozillaCookieJar(filename)
handler = request.HTTPCookieProcessor(cookie)
opener = request.build_opener(handler)
response = opener.open('http://hd.sz189.cn/huodong/bestPartner.shtml?action=rankList&openid=ohVEEj8r3W5akutdRmhsqIta_Ta1187')
cookie.load(filename, ignore_discard=True, ignore_expires=True)
response = opener.open('http://www.baidu.com')
login_url = 'http://hd.sz189.cn/huodong/bestPartner.shtml?action=addPopularityAjax'
user_agent = r'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'
head = {'User-Agnet': user_agent, 'Connection': 'keep-alive'}
Login_Data = {'openid':'ohVEEj8r3W5akutdRmhsqIta_Ta1187' ,'voteOpenid':'ohVEEj_pAamlNxqtmahk_L8UeU8Q', 'time' : '1530772451922'   }

logingpostdata = urllib.parse.urlencode(Login_Data).encode('utf-8')
req1 = request.Request(url=login_url, data=logingpostdata, headers=head)
response1 = opener.open(req1)
print(response1.read().decode('utf-8'))
