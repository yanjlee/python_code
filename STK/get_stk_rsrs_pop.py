# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
# from datetime import timedelta, datetime as dt
from ConnectDB import get_data
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

def Run(dataset,df_return,S):
    #实参数据定义##########################
    FEE = 0.0016

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

    # 策略和类初始化数据
    stk_list=['']
    cumulative_return = [1.0]
    return_list= [0]

    for i, row in enumerate(df.iterrows()):
        if df.iloc[i].max(axis=None, skipna=True) > S:
            stk_list.append(df.iloc[i].idxmax(axis=None, skipna=True))
        else:
            stk_list.append('')

        if i < 1:  # 从第二条开始
            continue

        if len(stk_list[-2]) > 1:
            chg = df_return.iloc[i][stk_list[-2]]
            if stk_list[-2] == stk_list[-3]:
                return_list.append(chg)
            else:
                return_list.append(chg - FEE) # 换仓，交易手续费
            # cumulative_return.append(round(cumulative_return[-1] * (1 + return_list[-1]), 5))
            cumulative_return.append(cumulative_return[-1] * (1 + return_list[-1]))
        else:
            cumulative_return.append(cumulative_return[-1])
            return_list.append(0)

    stk_list.pop()

    # 结果统计与展示
    df_rt = pd.DataFrame({'datetime':list(df.index),'cum_rate':cumulative_return,'stk_list':stk_list,'return_list':return_list})
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    df_rt['cum_rate'].plot()
    # plt.plot(df_rt['datetime'], df_rt['cum_rate'])
    df_rt = df_rt.set_index('datetime')
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
    idx = list(df.datetime[N:])
    cx = []
    # rsquareds = []
    for i in range(len(df)-N):
        if len(df) <= N:
            continue
        x = sm.add_constant(np.array(df.low[i:i+N],dtype=float))
        y = np.array(df.high[i:i+N],dtype=float)
        regr = sm.OLS(y, x)
        res = regr.fit()
        cx.append(round(res.params[-1],4))
        # rsquareds.append(round(res.rsquared,4))
    # cx = get_median_filtered(list(cx),6) # MAD去极值
    zs_idx = idx[M:]
    zs = [] # zscore
    for j in range(len(cx)-M):
        if len(cx) <= M:
            continue
        zs.append(zscore(cx[j:j+M]))
    ols = {'datetime':zs_idx,'zs':zs}
    df_ols = pd.DataFrame(ols).set_index('datetime')
    return df_ols

# N = 32
# S = 0.0
# atr_n = 20
s_time = '2017-01-01'
e_time = '2019-02-26'
total_return = []
return_m = []
symbol_idx = 'SHSE.000300'
# symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600585','SHSE.600660','SHSE.603288']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260',
symbol_list = ['SHSE.510050','SHSE.510500','SHSE.510880','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.518880'\
    ,'SHSE.600036','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
    ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
    ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
    ,'SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
    ,'SZSE.002508','SZSE.002555','SZSE.002572','SZSE.002833','SZSE.159901','SZSE.159915','SZSE.159919']
# symbol_list = ['SZSE.002456','SZSE.000333']
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
# df_idx = get_k(symbol_idx, 60, 0, start_year, end_year).drop(['open', 'high', 'low', 'close'], axis=1, inplace=False).set_index('datetime')

index_data  = get_data('date', 'idx_price', '\'000300.SH\'', start_year, end_year)
df_idx = pd.DataFrame(list(index_data),columns=['datetime']).set_index('datetime')

df_return = copy.copy(df_idx)

# s_list = np.arange(0,1.00,0.1)
S = 0
for N in range(5,32):
    df_i = copy.copy(df_idx)
    df_ret = copy.copy(df_return)
    for sym in symbol_list:
        sym = sym.replace('SHSE.', '').replace('SZSE.', '')
        if sym.startswith('6'):
            sym = '\'' + sym + '.SH\''
            price_data = get_data('date, high,low, close', 'stk_price_forward', sym, start_year, end_year)
        elif sym.startswith('0') or sym.startswith('3'):
            sym = '\'' + sym + '.SZ\''
            price_data = get_data('date,high,low, close', 'stk_price_forward', sym, start_year, end_year)
        elif sym.startswith('1') or sym.startswith('5'):
            sym = '\'' + sym + '.OF\''
            price_data = get_data('date,high,low, close', 'etf_price', sym, start_year, end_year)
        # if sym.startswith('SHSE'):
        #     sym =  sym.replace('SHSE.','\'') + '.SH\''
        # else:
        #     sym =  sym.replace('SZSE.','\'') + '.SZ\''
        # price_data  = get_data('date, open, high, low ,close', 'stk_price_forward', sym, start_year, end_year)
        df_data = pd.DataFrame(list(price_data),columns=['datetime','high','low','close'])


    # 查询历史行情
    #     df_k = history(symbol=sym, frequency='1h', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
    #     df_data = get_k(sym, 60, 0, start_year, end_year)
        if len(df_data) == 0:
            continue
        # df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
        df_data.loc[:, 'chg'] = (df_data['close'] - df_data['close'].shift(1)) / df_data['close'].shift(1)
        df_data.chg = df_data.chg.astype(float).round(5)
        df_rsrs = ols_rsrs(N, 2 * N, df_data[['datetime','high', 'low']])


        df_i = pd.concat([df_i, copy.copy(df_rsrs.rename(columns={'zs':sym.replace('\'','')}))],sort=True, axis=1).fillna(0)
        df_ret= pd.concat([df_ret, copy.copy(df_data.set_index('datetime').drop([ 'high', 'low', 'close'],axis=1,inplace=False)\
                                             .rename(columns={'chg':sym.replace('\'','')}))],sort=True, axis=1).fillna(0)
        df_ret = df_ret.loc[df_i.index].fillna(0)

        # df_k = df_k.dropna()
        # cci_n= [15, 30, 60]
        # cci_m = pd.DataFrame()
        # for n in cci_n:
        #     cci_m = pd.concat([cci_m, ta_cci(n,df_data)], axis=1)
        # df_data =  pd.concat([df_data, cci_m], axis=1)

        # DrawSignals(df_data)


    for S in s_list:
        re, mdd, df_r = Run(df_i,df_ret,S)
        total_return.append([N,S,re,mdd])
# print('TotalReturn: '+ str(re) + ' MaxDrawDown: ' + str(mdd))
print(total_return)
ret = pd.DataFrame(total_return, columns=['N','S', 'return', 'mdd'])
# # # print(ret)

filename = time.strftime('%Y%m%d_%H%M%S') + '.csv'
ret.to_csv(filename)