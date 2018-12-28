# -*- coding:utf-8 -*-
# Author:OpenAPISupport@wind.com.cn  
# Editdate:2017-09-06
# 绘制k线图

# 启动WindPy
from CIGRG.WindPy import *

w.start()

import datetime

from matplotlib.dates import DateFormatter
from matplotlib.finance import candlestick_ohlc
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

dailyQuota = w.wsd("002456.SZ", "open,high,low,close", "ED-1Y",
                   (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'), "Fill=Previous")

tupleQuota = []
for i in range(len(dailyQuota.Data[0])):
    tupleQuota.append((dailyQuota.Times[i].toordinal(), dailyQuota.Data[0][i], dailyQuota.Data[1][i],
                       dailyQuota.Data[2][i], dailyQuota.Data[3][i]))

mondayFormatter = DateFormatter('%Y-%m-%d')  # 如：2015-02-29
fig, ax = plt.subplots()
ax.xaxis.set_major_formatter(mondayFormatter)
candlestick_ohlc(ax, tupleQuota, width=0.2, colorup='r', colordown='g')

plt.title(u'欧菲科技 002456')
plt.show()
