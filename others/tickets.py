# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import tushare as ts
df = ts.realtime_boxoffice()
print(df)

# ds = ts.get_notices()
# print(ds)

# da = ts.get_latest_news() #默认获取最近80条新闻数据，只提供新闻类型、链接和标题
# dc = ts.get_latest_news(top=5,show_content=True) #显示最新5条新闻，并打印出新闻内容
#
# print(da)
# print(dc)
