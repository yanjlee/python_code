# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
# from datetime import timedelta, datetime as dt
import time
import talib as ta
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import numpy as np
from STK.tsdata import get_k_stk as get_k
import statsmodels.api as sm # 最小二乘
import copy
#from statsmodels.stats.outliers_influence import summary_table # 获得汇总信息
#from sklearn.preprocessing import MinMaxScaler, StandardScaler



# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

def Run(dataset,S):
    #实参数据定义##########################
    FEE = 0
    units = 2000

    def MaxDrawDown(return_list):
        max_value = 0
        mdd = 0
        for i in return_list:
            max_value = max(i, max_value)
            if max_value != 0:
                mdd = round(min(mdd, (i - max_value) / max_value),3)
            else:
                mdd = 0
        return(mdd)

    # 获取数据, 创建DataFrame
    df = dataset

    # 定义账户类
    class ActStatus:
        def __init__(self):
            self.datetime = ''
            self.close = 0
            self.chg = 0
            self.pos = 0 # 1 long，-1 short，0 empty
            self.pre_pos = 0

            self.pnl = 0
            self.fee = 0
            self.net_pnl = 0
            self.pnl_rate = 0

        def trade_calc(self, datetime, close, chg, signal, pre_pos):
            self.datetime =datetime
            self.close = close
            self.chg = chg
            self.pos = signal
            self.pre_pos = pre_pos

            self.pnl = self.chg * self.pos * units * self.close
            self.fee = max(abs(self.close * units * abs(self.pos - self.pre_pos)) * FEE, 5 * abs(self.pos - self.pre_pos))
            self.net_pnl = self.pnl - self.fee
            self.pnl_rate = (self.chg - FEE) * self.pos


    # 策略和类初始化数据
    signal = 0
    pre_pos = 0
    rt_list = []
    atr = df.atr.iloc[0]
    pre_close = df.close.iloc[0]
    max_price = 0
    buy_price = 0
    b_day = 0

    # cci_col = []
    # for c in cci_n:
    #     cci_col.append('cci' + str(c))
    # pre_cci_list = list(df[cci_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[1].datetime
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        b_day = max(b_day - 1, 0)
        # cci_list = list(row[1][cci_col])
        zs_value = row[1].zs

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos


    ## 策略信号
        # signal_list = []
        #
        # ## CCI策略
        # for j in range(0, len(cci_n)):
        #     pre_cci = pre_cci_list[j]
        #     cci = cci_list[j]
        #     ci = 400
        #     range_value = 50
        #     for i in range(-ci, ci + 1, range_value):
        #         if pre_cci < i and cci > i:
        #             signal_list.append(1)
        #         elif pre_cci > i and cci < i:
        #             signal_list.append(-1)
        #         else:
        #             signal_list.append(pre_pos)
        #
        # signal_value = sum(signal_list)  # 计算产生总信号
        # if signal_value > 0:
        #     signal_cci = 1
        # elif signal_value < 0:
        #     signal_cci = 0
        # else:
        #     signal_cci = pre_pos

        if zs_value > -S :
            signal_rs = 1
        elif zs_value < -S:
            signal_rs = 0
        else:
            signal_rs = pre_pos

        if signal_rs == 1:# or signal_cci == 1:
            signal = 1
        elif signal_rs == 0:# and signal_cci == 0:
            signal = 0
        else:
            signal = pre_pos

            # ATR 止损
        if signal == 1:
            max_price = max(max_price, row[1].high)
        else:
            max_price = 0

        if close < (max_price - 2.2 * atr) and signal == 1:
            signal = 0
        elif b_day != 0:
            signal = 0

        # 百分比止损
        stop_loss = 0.05
        if signal == 1 and close < buy_price * (1 - stop_loss):
            signal = 0
        if pre_pos == 0 and signal == 1:
            buy_price = pre_close
        elif pre_pos == 1 and signal == 0:
            buy_price = 0
            b_day = 3

        ## 保留前一天close数据
        pre_close = close
        # pre_cci_list = cci_list


    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    # df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    df_rt['cum_rate'].plot()
    df_rt = df_rt.set_index('datetime')
    # df = df.set_index('datetime')
    # df_rt = pd.concat([df_rt, df], axis=1)
    # df_rt.to_csv('test.csv')
    # print(df_rt)
    return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)


def DrawSignals(k_data):
    # 作图
    stick_freq = 20 # 横坐标间隔

    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(k_data[['datetime','open','high','low','close']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(ndays)

    left, width = 0.05, 0.90 ## 定义图横向使用
    rect1 = [left, 0.38, width, 0.60] ## 第一框图高度从0.38~0.98
    rect2 = [left, 0.08, width, 0.30] ## 第3框图高度从0.08~0.38，余下留给了横坐标

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['zs']*100, color='red', label='zs')
    ax2.axhline(80, linestyle='dotted', color='m', lw=0.5)  ## 画一条水平收益基准线
    ax2.axhline(-80, linestyle='dotted', color='b', lw=0.5)  ## 画一条水平收益基准线
    ax2.legend(loc='upper left', frameon=False)

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化
    ax2.grid(True, linestyle='dotted', linewidth='0.5')

    for label in ax.get_xticklabels():
        label.set_visible(False) ## 隐藏第一框图横坐标
    plt.show()

def DrawSignals2(k_data):
    # 作图
    stick_freq = 20 # 横坐标间隔

    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(k_data[['datetime','open','high','low','close']])
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

    ax3.plot(date_strings, k_data['cum_rate'], color='blue', label='c_return')
    ax3.axhline(1, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.legend(loc='upper left', frameon=False)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['cci30'], color='green', label='cci30')
    ax2.plot(date_strings, k_data['cci60'], color='red', label='cci60')
    ax2.legend(loc='upper left', frameon=False)
    ax2.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())
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

def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))

def get_median_filtered(signal, threshold=3):
    signal = signal.copy()
    median_value = np.median(signal)
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)
    up_median = median_value + threshold*median_difference
    down_median = median_value - threshold*median_difference
    for i in range(len(signal)):
        if signal[i] > up_median:
            signal[i] = up_median
        elif signal[i] < down_median:
            signal[i] = down_median
    return signal

def zscore(dataset):
    data_mean = np.mean(dataset)
    data_std = np.std(dataset)
    z_values = (dataset-data_mean)/data_std
    # return z_values
    return z_values[-1]

def ols_rsrs(N,M,df):
    idx = list(df.index[N:])
    cx = []
    rsquareds = []
    for i in range(len(df)-N):
        if len(df) <= N:
            continue
        x = sm.add_constant(list(df.low[i:i+N]))
        y = list(df.high[i:i+N])
        regr = sm.OLS(y, x)
        res = regr.fit()
        cx.append(round(res.params[-1],4))
        rsquareds.append(round(res.rsquared,4))
    # cx = get_median_filtered(list(cx),6) # MAD去极值
    zs_idx = idx[M:]
    zs = [] # zscore
    # zm = [] # zscore_modified
    # zmps = [] # zscore_modified_positive_skewness
    for j in range(len(cx)-M):
        if len(cx) <= M:
            continue
        zs.append(zscore(cx[j:j+M]))
        # zm.append(zs[-1] * rsquareds[j+M])
        # zmps.append(zm[-1] * cx[j+M])
    ols = {'idx':zs_idx,'zs':zs}
    df_ols = pd.DataFrame(ols).set_index('idx')
    return df_ols


atr_n = 20
s_time = '2014-10-01'
e_time = '2016-02-26'
total_return = []
return_m = []
# symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600585','SHSE.600660','SHSE.603288']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']
symbol_list = ['SZSE.002456']
# start_list = []
years = int(e_time[:4]) - int(s_time[:4]) + 1
# for n in range(years):
#     if n == 0:
#         start_year = s_time
#         end_year = str(int(s_time[:4]) + n) + '-12-31'
#     elif n == (years - 1):
#         start_year = str(int(s_time[:4]) + n) + '-01-01'
#         end_year = e_time
#     else:
#         start_year = str(int(s_time[:4]) + n) + '-01-01'
#         end_year = str(int(s_time[:4]) + n) + '-12-31'
#     # start_list.append(start_year)
start_year = s_time
end_year = e_time
# s_list = np.arange(0.75,1.00,0.05)

for sym in symbol_list:
# 查询历史行情
#     df_k = history(symbol=sym, frequency='1h', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
    df_data = get_k(sym, 60, 0, start_year, end_year)
    if len(df_data) == 0:
        continue
    df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
    df_data.loc[:, 'chg'] = (df_data['close'] - df_data['close'].shift(1)) / df_data['close'].shift(1)
    # df_data.loc[:,'ma5'] = df_data.close.rolling(5,min_periods=0).mean()
    # df_data.loc[:,'ma21'] = df_data.close.rolling(21,min_periods=0).mean()

    # cci_n= [15, 30, 60]
    # cci_m = pd.DataFrame()
    # for n in cci_n:
    #     cci_m = pd.concat([cci_m, ta_cci(n,df_data)], axis=1)
    # df_data =  pd.concat([df_data, cci_m], axis=1)


    # for N in [32]:#range(4,41):
    N = 20
    M = 2 * N
    S = 0.8
    df_k= copy.copy(df_data)
    df_rsrs = ols_rsrs(N,M,df_k[['high', 'low']])
    df_k = pd.concat([df_k,df_rsrs], axis=1)
    df_k = df_k.dropna()
    DrawSignals(df_k)
    # rsrs = ['zs']#,'zm','zmps']
    # df_run = df_k[['datetime','open','high','low','close','atr','chg']]
    # for rs in rsrs:
    #     df_run.loc[:,'rs'] = df_k[rs]

    # re, mdd, df_r = Run(df_k,S)
    # total_return.append([sym,re,mdd])
    # print(total_return[-1])
#
# ret = pd.DataFrame(total_return, columns=['symbol','N','rs_name', 'return', 'mdd'])
# # print(ret)
#
# # filename = time.strftime('%Y%m%d_%H%M%S') + '.csv'
# # t_r=pd.DataFrame(list(total_return))
# # t_r.to_csv(filename)