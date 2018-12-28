from datetime import datetime, timedelta
import pandas as pd
from ConnectDB import get_all_data
import math
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import numpy as np
import talib as ta

# import matplotlib.pyplot as plot
# from decimal import Decimal
# import numpy as np
# import scipy as sp
# from scipy.optimize import leastsq

# 生成K线时间轴
def TimeList(n, e_time):
    day_list = []
    for i in range(0, 360):
        times = (datetime.strptime('09:00', '%H:%M') + timedelta(minutes=i)).strftime('%H:%M')
        if (times >= '10:15' and times < '10:30') or (times >= '11:30' and times < '13:30'):
            continue
        day_list.append(times)

    e_time = e_time
    night_list = []
    if e_time == '23:00':
        k = 120
    elif e_time == '23:30':
        k = 150
    elif e_time == '01:00':
        k = 240
    elif e_time == '02:30':
        k = 330
    elif e_time == '15:00':
        k = 0
    else:
        k = 0
    for j in range(0, k):
        times = (datetime.strptime('21:00', '%H:%M') + timedelta(minutes=j)).strftime('%H:%M')
        night_list.append(times)

    def k_time(n, time_list):
        k_list = []
        for s in range(0, n):
            temp_list = []
            for t in range(s, len(time_list), n):
                temp_list.append(time_list[t])
            k_list.append(temp_list)
        return (k_list)

    day_time = k_time(n, day_list)
    night_time = k_time(n, night_list)
    return (day_time, night_time)


# 获取数据
def get_data(symbol, start_time, end_time):
    items = 'datetime, open, high, low, close, volume'
    table = ' fur_price_1m'
    condition = 'where symbol = \'' + symbol + '\' and datetime >= \'' + start_time + '\' and datetime <= \'' + end_time + '\'  order by datetime asc'
    symbol_data = get_all_data(items, table, condition)
    k_data = pd.DataFrame(list(symbol_data), columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    k_data.set_index(["datetime"], inplace=True)

    k_days = list(k_data.index.strftime('%Y-%m-%d'))
    # k_days = list(k_data.index[:10])
    k_days = sorted(set(k_days), key=k_days.index)
    return (k_data.astype('float64'), k_days)


# k线价格聚合
def k_line(k, k_data, k_days, day_list, night_list):
    df_k = pd.DataFrame()

    def PreMin(times):
        pre_time = (datetime.strptime(times, '%Y-%m-%d %H:%M') + timedelta(minutes=-1)).strftime('%Y-%m-%d %H:%M')
        return (pre_time)

    for dates in k_days:
        # 生成日盘和夜盘的时间列表
        day_time_list = []
        night_time_list = []
        for dt in day_list[k]:
            day_time_list.append(dates + ' ' + dt)
        for nt in night_list[k]:
            if nt >= '21:00':
                night_time_list.append(dates + ' ' + nt)
            else:
                night_time_list.append(
                    (datetime.strptime(dates, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d') + ' ' + nt)

        # 数据处理，生成日盘和夜盘的K线数据
        day_data = []
        for i in range(0, len(day_time_list) - 1):
            df_day = k_data.loc[day_time_list[i]:PreMin(day_time_list[i + 1])]
            if len(df_day) == 0:
                continue
            day_data.append([df_day.index[0].strftime('%Y-%m-%d %H:%M'), df_day.open[0], max(df_day.high),
                             min(df_day.low),df_day.close[-1],df_day.volume.sum()])
        try:
            temp_end = list(k_data.loc[day_time_list[-1]])
            temp_end.insert(0, day_time_list[-1])
            day_data.append(temp_end)
        except Exception as err:
            pass
            # print(err)
        day_data = pd.DataFrame(day_data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        day_data.set_index(["datetime"], inplace=True)

        night_data = []
        for j in range(0, len(night_time_list) - 1):
            df_day = k_data.loc[night_time_list[j]:PreMin(night_time_list[j + 1])]
            if len(df_day) == 0:
                continue
            night_data.append(
                [df_day.index[0].strftime('%Y-%m-%d %H:%M'), df_day.open[0], max(df_day.high), min(df_day.low),
                 df_day.close[-1],df_day.volume.sum()])
        try:
            temp_end_n = list(k_data.loc[night_time_list[-1]])
            temp_end_n.insert(0, night_time_list[-1])
            night_data.append(temp_end_n)
        except Exception as err:
            pass
            # print(err)
        night_data = pd.DataFrame(night_data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        night_data.set_index(["datetime"], inplace=True)

        df_k = pd.concat([df_k, day_data, night_data])
    return (df_k)


# 布林线计算
# def Bolling(n, k_data):  # n天的计算移动平均和标准差,以及布林线上下轨
#     # m = math.log(n, 4.68685)  # 标准差倍数
#     m = math.log(n) / 9 + 5 / 3  # 标准差倍数
#     bolling = pd.DataFrame()
#     # k_data['ema' + str(n)] = k_data.close.ewm(span=n, min_periods=0, ignore_na=True, adjust=True).mean()
#     bolling['ma' + str(n)] = k_data.close.rolling(window=n, min_periods=0, center=False).mean()
#     bolling['std' + str(n)] = k_data.close.rolling(window=n, min_periods=0, center=False).std()
#     # bolling['std_ma'] = bolling['std' + str(n)].rolling(window=n, min_periods=0, center=False).mean()
#     bolling['up'] = bolling['ma' + str(n)] + m * bolling['std' + str(n)]
#     bolling['down'] = bolling['ma' + str(n)] - m * bolling['std' + str(n)]
#     bolling['bp'] = (k_data.close - bolling.down) / 2 / m / bolling['std' + str(n)]
#     return (bolling.round(2))

def ta_bolling(n, k_data):
    m = math.log(n) / 9 + 5 / 3
    bolling = pd.DataFrame()
    bolling['up'], bolling['ma'], bolling['down'] = ta.BBANDS(k_data.close, timeperiod=n, nbdevup=m, nbdevdn=m, matype=0)
    bolling['std'] = (bolling.up - bolling.ma) / m / 2
    bolling['bp'] = (k_data.close - bolling.down) / bolling['std'] / m / 2
    return (bolling.round(2))

# CCI计算
# def CCI(n, k_data):
#     cci = pd.DataFrame()
#     cci['close'] = k_data.close
#     # cci['tp'] = (k_data.open + k_data.high + k_data.low + k_data.close) / 4
#     gs = 0.618
#     cci['tp'] = gs * k_data.close + (k_data.high + k_data.low + k_data.open) * (1 - gs) / 3
#     cci['ma'] = cci.tp.rolling(window=n, min_periods=0, center=False).mean()
#     cci['abs_value'] = abs(cci.ma - cci.close)
#     cci['md'] = cci.abs_value.rolling(window=n, min_periods=0, center=False).mean()
#     cci['cci'] = (cci.tp - cci.ma) / cci.md / 0.015
#     cci['cci']= cci.cci.apply(lambda x: x if x < 150 else 150).apply(lambda x: x if x > -150 else -150)
#     return(cci.cci.round(2))

def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    # cci['cci'] = cci.cci.rolling(window=3, min_periods=0, center=False).mean()
    return cci.round(2)

# ATR计算
# def ATR(n, k_data):
#     atr = pd.DataFrame()
#     i = 0
#     TR_l = [0]
#     while i < len(k_data.index) - 1:
#         TR = max(k_data['high'].iloc[i + 1], k_data['close'].iloc[i]) - min(k_data['low'].iloc[i + 1], k_data['close'].iloc[i])
#         TR_l.append(TR)
#         i = i + 1
#     TR_s = pd.DataFrame(TR_l, columns=['TR'], index=k_data.index)
#     # ATR = pd.Series(pd.ewm(TR_s, span=n, min_periods=n), name='ATR_' + str(n))
#     atr['atr' + str(n)] = TR_s['TR'].ewm(span=n, min_periods=0, adjust=True, ignore_na=False).mean()
#     return(atr['atr' + str(n)].round(2))

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    # atr['natr'] = ta.NATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))


# 计算BBI指标与BBIBolling线
# def BBI(k_Data):
#     bbi = pd.DataFrame()
#     # days = [3,6,12,24]
#     # for j in days:
#     #     bbi['ma' + str(j)] = k_data.close.rolling(window=j, min_periods=0, center=False).mean()
#     # bbi['bbi'] = bbi.apply(lambda x: x.sum()/4, axis=1)
#
#     fibo = [0,1,1,2,3,5,8,13,21,34,55,89,144,233,377]
#     for i in range(4,10):
#         bbi['ema' + str(fibo[i])] = k_data.close.ewm(span=fibo[i], min_periods=0, ignore_na=True, adjust=True).mean()
#     n = len(bbi.columns.values)
#     bbi['bbi'] = bbi.apply(lambda x: x.sum()/n, axis=1)
#
#     bbi['bbi_std'] = bbi.bbi.rolling(window=11, min_periods=0, center=False).std()
#     bbi['bbi_up'] = bbi.bbi + 6 * bbi.bbi_std
#     bbi['bbi_down'] = bbi.bbi - 6 * bbi.bbi_std
#     return(bbi[['bbi','bbi_up','bbi_down']].round(2))


# 计算 当日成交密度II%(Intraday Intensity)和集散量指标AD%(Accumulation Distribution)
def ADII(n, k_data):
    adii = pd.DataFrame()
    adii['vol_ii'] = k_data.volume * (2 * k_data.close - k_data.high - k_data.low) / (k_data.high - k_data.low + 0.0001 )
    adii['ii'] = adii.vol_ii.rolling(window=n, min_periods=0, center=False).sum() / k_data.volume.rolling(window=n, min_periods=0, center=False).sum()
    adii['vol_ad'] = k_data.volume * (k_data.close - k_data.open) / (k_data.high - k_data.low + 0.0001)
    adii['ad%'] = adii.vol_ad.rolling(window=n, min_periods=0, center=False).sum() / k_data.volume.rolling(window=n, min_periods=0, center=False).sum()
    return(adii[['ad%','ii']].round(3))

def ta_ad(k_data):
    ad = pd.DataFrame()
    ad['ad'] = ta.AD(k_data.high, k_data.low, k_data.close, k_data.volume)
    ad['ado'] = ta.ADOSC(k_data.high, k_data.low, k_data.close, k_data.volume,fastperiod=5, slowperiod=13)
    return(ad.round(2))

## 资金流向指标MFI(Money Flow Index)
# def MFI(n, k_data):
#     mfi = pd.DataFrame()
#     length = int(n/2)
#     gs = 0.618
#     mfi['typ'] = gs * k_data.close + (k_data.high + k_data.low + k_data.open) * (1-gs) / 3
#     mfi['in'] = 0
#     mfi['out'] = 0
#     mfi['test'] = mfi['typ'] > mfi['typ'].shift(1)
#     mfi['in'][mfi['typ'] > mfi['typ'].shift(1)] = mfi['typ'] * k_data.volume
#     mfi['out'][mfi['typ'] < mfi['typ'].shift(1)] = mfi['typ'] * k_data.volume
#     mfi['val'] = mfi['in'].rolling(window=length, min_periods=0, center=False).sum() / mfi['out'].rolling(window=length, min_periods=0, center=False).sum()
#     mfi['mfi'] = mfi.val.apply(lambda x: 100 - (100 / (x + 1 + 0.0001)) if x != float('inf') else 50)
#     mfi.mfi = mfi.mfi.fillna(50)
#     return(mfi.mfi.round(2))
##


def ta_mfi(n, k_data):
    mfi = pd.DataFrame()
    mfi['mfi'] = ta.MFI(k_data.high, k_data.low, k_data.close, k_data.volume, timeperiod=n)
    return(mfi.round(2))

## Stop and Reverse, 抛物线指标/停损转向操作点指标
def ta_sar(k_data):
    sar = pd.DataFrame()
    sar['sar'] = ta.SAR(k_data.high, k_data.low, acceleration=0.05, maximum=0.2)
    # sar['sar_e'] = ta.SAREXT(k_data.high, k_data.low, startvalue=0, offsetonreverse=0, accelerationinitlong=0.02, accelerationlong=0.02,
    #               accelerationmaxlong=0.2, accelerationinitshort=0.02, accelerationshort=0.02, accelerationmaxshort=0.2)
    return(sar.round(2))

## MACD - Moving Average Convergence/Divergence
def ta_macd(fp, sp, sgp, k_data):
    macd = pd.DataFrame()
    macd['diff'], macd['dea'], macd['hist'] = ta.MACDEXT(k_data.close, fastperiod=fp, fastmatype=0,
                                                                    slowperiod=sp, slowmatype=0, signalperiod=sgp,
                                                                    signalmatype=0)
    return(macd.round(2))
    # macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)


# # 作图和指标计算
# def Draw_Return(k_data):
#     # 作图
#     stick_freq = int(len(k_data.index) / 20) * 10  # 横坐标间隔
#     ## 数据清理，去除非交易时间
#     ohlc_data_arr = np.array(td_return[['datetime','td_revenue_cumu']])
#     ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
#     ohlc_data_arr3 = ohlc_data_arr2[:, 1]
#     ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
#     date_strings = list(df_data['datetime'])
#
#     left, width = 0.1, 0.8  ## 定义图横向使用
#     rect1 = [left, 0.4, width, 0.5]
#     rect2 = [left, 0.1, width, 0.3]
#
#     fig = plt.figure(facecolor='white')
#     axescolor = '#f6f6f6'  # the axes background color
#
#     ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
#     ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)
#     ax2.plot(date_strings, td_return['td_maxdrawdown'], color='g', label='MaxDrawDown', lw=1)
#     ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right')
#     ax2.legend(loc='center right', frameon=False)
#
#     ax.plot(date_strings,  ohlc_data_arr3, color='blue', label='Cumulative Return', lw=1)
#     # Format x axis
#     ax.set_xticks(ndays[::stick_freq])
#     ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
#     ax.set_xlim(ndays.min(), ndays.max())
#     ax.legend(loc='center left', frameon=False)
#     ax.autoscale_view()
#     ax.grid(True, linestyle='dotted', linewidth='0.5')  ## 背景格线虚化
#     for label in ax.get_xticklabels():
#         label.set_visible(False)  ## 隐藏第一框图横坐标
#
#     plt.show()


def DrawSignals(k_data):
    # 作图
    stick_freq = 20 # 横坐标间隔

    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(k_data.reset_index('datetime')[['datetime','open','high','low','close']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(ndays)

    left, width = 0.05, 0.90 ## 定义图横向使用
    rect1 = [left, 0.48, width, 0.50] ## 第一框图高度从0.48~0.98
    rect3 = [left, 0.28, width, 0.20] ## 第二框图高度从0.28~0.48，余下留给了横坐标
    rect2 = [left, 0.08, width, 0.20] ## 第3框图高度从0.08~0.28，余下留给了横坐标

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax)
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)
    ax2t = ax2.twinx() ## 右侧镜像纵坐标

    ax3.plot(date_strings, k_data['ii'], color='red', label='II%')
    ax3.plot(date_strings, k_data['ad%'], color='green', label='AD%')
    ax3.plot(date_strings, k_data['mfi'] / 100 - 0.5, color='blue', label='MFI')
    ax3.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.axhline(0.15, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.legend(loc='upper left', frameon=False)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['bp'] * 100, color='red', label='bp%')
    ax2.plot(date_strings, k_data['mfi'], color='blue', label='mfi')
    # ax2.plot(date_strings, k_data['cci'], color='blue', label='cci')
    ax2.legend(loc='lower left', frameon=False)

    ax2t.set_ylim(float(min(k_data.cci)), float(max(k_data.cci)))
    ax2t.plot(date_strings, k_data['cci'], color='green', label='cci')
    ax2t.legend(loc='upper left', frameon=False)
    ax2t.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    ax.plot(date_strings, k_data['ma20'], color='m', label='MA20')
    ax.plot(date_strings, k_data['up'], color='blue', label='Bolling_up')
    ax.plot(date_strings, k_data['down'], color='brown', label='Bolling_down')
    # ax.plot(date_strings, k_data['sar'], marker = '*',color='olive', label='SAR', lw=0.5)
    ax.legend(loc='upper left', frameon=False)

    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化
    ax2.grid(True, linestyle='dotted', linewidth='0.5')
    ax3.grid(True, linestyle='dotted', linewidth='0.5')

    for label in ax.get_xticklabels():
        label.set_visible(False) ## 隐藏第一框图横坐标
    for label in ax3.get_xticklabels():
            label.set_visible(False)  ## 隐藏第一框图横坐标
    plt.show()



def Get_k(start, end, symbol):
    kn = 28
    td_time = '23:00'
    # n = 20  # 指数移动平均间隔
    # symbol = 'RB'
    # start_time = '2016-12-04 09:00:00'
    # end_time = '2016-12-06 15:00:00'
    # n = n  # 指数移动平均间隔
    symbol = symbol
    start_time = start
    end_time = end

    day_list, night_list = TimeList(kn, td_time)
    k_data, k_days = get_data(symbol, start_time, end_time)
    # df = k_data.copy()
    df_k = k_line(0, k_data, k_days, day_list, night_list)
    return(df_k)

def Calc_k(n,k_data):
    # k_data = pd.concat([k_data, ta_bolling(n,k_data), ta_cci(n,k_data), ta_atr(n,k_data), ta_ad(k_data), ta_mfi(n,k_data), ta_sar(k_data), ADII(n,k_data)], axis=1)
    k_data = pd.concat([k_data, ta_cci(n,k_data), ta_atr(n,k_data)], axis=1)
    # k_data = k_data.dropna()
    # k_data = pd.concat([k_data, ta_macd(13,21,8,k_data)], axis=1)
    # k_data = pd.concat([k_data, Bolling(n, k_data), CCI(n, k_data), ATR(n, k_data), BBI(k_data), ADII(n, k_data), MFI(n, k_data), SAR(k_data)], axis=1)
    # print(k_data.columns.values)
    # DrawSignals(k_data)
    return(k_data)


# n = 13
# start = '2016-12-04 09:00:00'
# end = '2016-12-09 15:01:00'
# symbol = 'RB'
# K_data(n, start, end, symbol)