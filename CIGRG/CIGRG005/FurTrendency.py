# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from ConnectDB import connDB, connClose, get_data, get_all_data
import pandas as pd
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
import matplotlib.dates as mdates
from matplotlib.dates import MONDAY, DateFormatter, DayLocator, WeekdayLocator
from decimal import Decimal

####################
freq = 1
fee = 0.00002
leverage = 1/0.11
ema=[5,21,55]


conn, cur = connDB()

future_code ='RB1810.SHF'
# 选出收盘价在20/60日均线之上的指数
req_sql = 'SELECT datetime, open, high, low, close FROM data.fur_price where symbol =\'' + future_code + '\' and datetime >= \'2018-05-01\' and datetime <= \'2018-05-8\';'

try:
    cur.execute(req_sql)
    future_data = cur.fetchall()
except Exception as e:
    print(e)

## 数据汇集
price_list = []
for i in range(0, len(future_data), freq):
    day_list = []
    day_list.append(future_data[i][0].strftime('%m-%d %H:%M')) # datetime
    day_list.append(Decimal(future_data[i][1])) # open
    high_temp = future_data[i][2]
    low_temp = future_data[i][3]
    if i + freq <= len(future_data):
        for j in range(i, i+freq):
            high_temp = max(high_temp, future_data[j][2])
            low_temp = min(low_temp, future_data[j][3])
        day_list.append(Decimal(high_temp)) # high
        day_list.append(Decimal(low_temp)) # low
        day_list.append(Decimal(future_data[i+freq-1][4])) # close
    else:
        for j in range(i, len(future_data)):
            high_temp = max(high_temp, future_data[j][2])
            low_temp = max(low_temp, future_data[j][3])
        day_list.append(high_temp) # high
        day_list.append(low_temp) # low
        day_list.append(future_data[-1][4]) # close
    price_list.append(day_list)

df_data = pd.DataFrame(price_list, columns=['datetime','open','high','low','close'])

## 计算EMA
for ma in ema:
    df_data['ema' + str(ma)] = df_data['close'].ewm(span=ma, min_periods=0, adjust=True, ignore_na=False).mean()

# 计算中心线ACE
df_data['ace'] = Decimal('0.1') * (df_data['high'] + df_data['low']) + Decimal('0.3') * df_data['open'] + Decimal('0.5') * df_data['close']

# 交易信号
td_data = pd.DataFrame(df_data['datetime'], columns=['datetime'])
td_signal = []

# ## 1. ema长短线
# for j in range(0, len(df_data)):
#     if min(df_data['close'][j], df_data['open'][j]) > max(df_data['ema21'][j], df_data['ema55'][j]):
#         if df_data['ace'][j] > df_data['ema5'][j]:
#             td_signal.append(-1)
#         else:
#             td_signal.append(0)
#     elif max(df_data['close'][j], df_data['open'][j]) < min(df_data['ema21'][j], df_data['ema55'][j]):
#         if df_data['ace'][j] < df_data['ema5'][j]:
#             td_signal.append(1)
#         else:
#             td_signal.append(0)
#     else:
#         td_signal.append(0)

###2. ACE与EMA短线
for j in range(0, len(df_data)):
    if df_data['ace'][j] > df_data['ema5'][j]:
        td_signal.append(-1)
    else:
        td_signal.append(1)


### 14:57及以后的3分钟，不交易，清仓
for k in range(0, len(df_data)):
    if df_data['datetime'][k][-5:] >= '22:57':
        td_signal[k] = 0

td_signal[-1] = 0 # 最后与1笔交易，清盘
td_data['td_signal'] = td_signal

## signle cumulation testing

# td_signal_a = []
# td_signal_a.append(td_signal[0])
# for a in range(1, len(td_signal)):
#     if td_signal[a] == 0:
#         td_signal_a.append(0)
#     else:
#         td_signal_a.append(td_signal[a] + td_signal_a[a-1])
#
# td_signal_b = []
# for b in td_signal_a:
#     if b >= 5:
#         td_signal_b.append(1)
#     elif b <= -5:
#         td_signal_b.append(-1)
#     else:
#         td_signal_b.append(0)
#
# td_data['td_signal_b'] = td_signal_b

## 计算算法的绩效如何
td_revenue = [0]
for k in range(1, len(td_data['td_signal'])):
    if td_data['td_signal'][k-1] == 1:
        td_revenue.append(round((df_data['close'][k] - df_data['close'][k-1]) * (1 - Decimal(fee)) * Decimal(leverage) / df_data['close'][k-1],4))
    elif td_data['td_signal'][k-1] == -1:
        td_revenue.append(round((df_data['close'][k-1] - df_data['close'][k]) * (1 - Decimal(fee)) * Decimal(leverage) / df_data['close'][k-1],4))
    else:
        td_revenue.append(0)

td_data['td_revenue'] = td_revenue # 每段收益
td_up = pd.DataFrame(list(td_data['td_revenue']), columns=['td_revenue'], index=td_data['datetime'])
td_up[ td_up < 0] = 0 # 正收益
td_down = pd.DataFrame(list(td_data['td_revenue']), columns=['td_revenue'], index=td_data['datetime'])
td_down[ td_down > 0] = 0 # 负收益

td_cumu = [1]
for j in td_revenue[1:]:
    td_cumu.append(round((td_cumu[-1] + j), 4))

td_return = pd.DataFrame(df_data['datetime'], columns=['datetime'])
td_return['td_revenue_cumu'] = td_cumu # 累计收益

## 计算最大回撤
max_dd = [0]
for x in range(1, len(td_cumu)):
    if max(td_cumu[0:x]) != 0:
        temp = (td_cumu[x] - max(td_cumu[0:x])) / max(td_cumu[0:x])
        if temp <= 0:
            max_dd.append(round(temp, 4))
        else:
            max_dd.append(0)
    else:
        max_dd.append(round(-max(td_cumu[0:x]), 4))

td_return['td_maxdrawdown'] = max_dd

print('Cumulative Return: ' + str(float(td_cumu[-1])))
print('Max Draw Down: ' + str(float(min(max_dd))))

def Draw_Return():
    # 作图
    stick_freq = int(len(td_return) / 20) * 10  # 横坐标间隔
    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(td_return[['datetime','td_revenue_cumu']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ohlc_data_arr3 = ohlc_data_arr2[:, 1]
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(df_data['datetime'])

    left, width = 0.1, 0.8  ## 定义图横向使用
    rect1 = [left, 0.4, width, 0.5]
    rect2 = [left, 0.1, width, 0.3]

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)
    ax2.plot(date_strings, td_return['td_maxdrawdown'], color='g', label='MaxDrawDown', lw=1)
    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right')
    ax2.legend(loc='center right', frameon=False)

    ax.plot(date_strings,  ohlc_data_arr3, color='blue', label='Cumulative Return', lw=1)
    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())
    ax.legend(loc='center left', frameon=False)
    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5')  ## 背景格线虚化
    for label in ax.get_xticklabels():
        label.set_visible(False)  ## 隐藏第一框图横坐标

    plt.show()



def Draw_Candles():
    ## 转换数列，在图标上标记出多空平与反转
    td_long = pd.DataFrame(columns=['datetime', 'price'])
    td_short = pd.DataFrame(columns=['datetime', 'price'])
    td_draw = pd.DataFrame(columns=['datetime', 'price'])
    td_rev = pd.DataFrame(columns=['datetime', 'price'])
    for m in range(1, len(td_data['td_signal'])):
        temp = pd.DataFrame({'datetime': df_data['datetime'][m], 'price': df_data['open'][m]},index=["0"])
        if td_data['td_signal'][m-1] == 1 and td_data['td_signal'][m] == 1:
            td_long = td_long.append(temp, ignore_index=True)
        elif td_data['td_signal'][m-1] == -1 and td_data['td_signal'][m] == -1:
            td_short = td_short.append(temp, ignore_index=True)
        elif abs(td_data['td_signal'][m-1]) == 1 and td_data['td_signal'][m] == 0:
            td_draw = td_draw.append(temp, ignore_index=True)
        elif td_data['td_signal'][m-1] * td_data['td_signal'][m] == -1:
            td_rev = td_rev.append(temp, ignore_index=True)

    # 作图
    stick_freq = 10 # 横坐标间隔
    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(df_data[['datetime','open','high','low','close']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(df_data['datetime'])

    left, width = 0.05, 0.90 ## 定义图横向使用
    rect1 = [left, 0.33, width, 0.65] ## 第一框图高度从0.33~0.98
    rect2 = [left, 0.08, width, 0.25] ## 第二框图高度从0.08~0.33，余下留给了横坐标

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)
    ax2t = ax2.twinx() ## 右侧镜像纵坐标

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.bar(td_up.index, td_up['td_revenue'], facecolor='red', edgecolor='white') ## 上收益柱图
    ax2.bar(td_down.index, td_down['td_revenue'], facecolor='green', edgecolor='white') ## 下损益组图
    ax2.axhline(0, color='k', lw=0.5) ## 中轴零线

    # 绘制成功率图像
    ax2t.set_ylim(float(min(td_cumu)), float(max(td_cumu)))
    ax2t.plot(td_return.index, td_return['td_revenue_cumu'], color='blue',   linewidth=1) ## 绘制右侧镜像纵坐标定义的累积收益曲线
    ax2t.axhline(0, linestyle='dotted', color='m', lw=0.8)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    # 画ema线，并标注
    ax.plot(date_strings, df_data['ema5'], color='m', label='EMA5', lw=1.2)
    ax.plot(date_strings, df_data['ema21'], color='blue', label='EMA21', lw=1)
    ax.plot(date_strings, df_data['ema55'], color='brown', label='EMA55', lw=1.2)
    ax.plot(date_strings, df_data['ace'], color='orange', label='ace', lw=1)
    # ax.legend(loc='upper left', frameon=False)
    # 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'
    # {'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive','tab:cyan'}

    # 标记多空平仓和反转等信号
    ax.plot(td_long['datetime'], td_long['price']+5, '^', label='Long', c = 'r')
    ax.plot(td_short['datetime'], td_short['price']+5, 'v', label='Short', c = 'g')
    ax.plot(td_draw['datetime'], td_draw['price']+5, 'x', label='Draw', c = 'k')
    ax.plot(td_rev['datetime'], td_rev['price']+5, 'd', label='Rev', c = 'b')
    ax.legend(loc='upper right', frameon=False)

    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化

    for label in ax.get_xticklabels():
        label.set_visible(False) ## 隐藏第一框图横坐标

    plt.show() ## 秀


connClose(conn, cur)
# Draw_Return()
Draw_Candles()
# connClose(conn, cur)