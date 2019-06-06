# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta, datetime as dt
import talib as ta
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import numpy as np
from STK.tsdata import get_k_stk as get_k, get_stk
import statsmodels.api as sm # 最小二乘
import copy

# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')


def MaxDrawDown(return_list):
    max_value = 0
    mdd = 0
    for i in return_list:
        max_value = max(i, max_value)
        if max_value != 0:
            mdd = round(min(mdd, (i - max_value) / max_value), 3)
        else:
            mdd = 0
    return (mdd)

def DrawSignals(k_data):
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
    ax2t = ax2.twinx() ## 右侧镜像纵坐标

    ax3.plot(date_strings, k_data['ii'], color='red', label='II%')
    ax3.plot(date_strings, k_data['ad%'], color='green', label='AD%')
    ax3.plot(date_strings, k_data['mfi'] / 100 - 0.5, color='blue', label='MFI')
    ax3.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.axhline(0.15, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.legend(loc='upper left', frameon=False)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['bp'] * 100, color='red', label='bp%')
    # ax2.plot(date_strings, k_data['mfi'], color='blue', label='mfi')
    # ax2.plot(date_strings, k_data['cci'], color='blue', label='cci')
    ax2.legend(loc='upper left', frameon=False)

    ax2t.set_ylim(float(min(k_data.cci)), float(max(k_data.cci)))
    ax2t.plot(date_strings, k_data['cci'], color='green', label='cci')
    ax2t.legend(loc='upper right', frameon=False)
    ax2t.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    ax.plot(date_strings, k_data['ma'], color='m', label='MA')
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

def cci_filter(df):
    cci_dict = {}
    for i, row in enumerate(df.iterrows()):
        cci_dict[row[0]] = list(row[1][row[1] == 1].index)
    return cci_dict

def cci_calc(df,sym):
    df_k = df.fillna(0)
    cci_n = [15, 30, 60]
    cci_m = pd.DataFrame(df_k.index).set_index('datetime')
    for n in cci_n:
        cci_m = pd.concat([cci_m, ta_cci(n, df_k)], axis=1)
    # k_data =  pd.concat([df_k, ta_atr(20,df_k), cci_m], axis=1)
    cci_m = cci_m.dropna()
    cci_sig = [0]
    cci_col = []
    pre_pos = 0
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(cci_m[cci_col].iloc[0])
    for i, row in enumerate(cci_m.iterrows()):
        cci_list = list(row[1][cci_col])
        if i < 1:  # 从第二条开始
            continue
        signal_list = []
        ## CCI策略
        for j in range(0, len(cci_n)):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            ci = 400
            range_value = 50
            for i in range(-ci, ci + 1, range_value):
                if pre_cci < i and cci > i:
                    signal_list.append(1)
                elif pre_cci > i and cci < i:
                    signal_list.append(-1)
                else:
                    signal_list.append(pre_pos)
        signal_value = sum(signal_list)  # 计算产生总信号
        if signal_value > 0:
            signal = 1
        elif signal_value < 0:
            signal = 0
        else:
            signal = pre_pos
        cci_sig.append(signal)
        pre_cci_list = cci_list
    cci_m[sym] = cci_sig
    return cci_m.drop(cci_col, axis=1, inplace=False)

def clean(df):
    drop_list = []
    for dtime in list(df.index):
        # if dtime[14:] not in ['00:00', '30:00']:
        if dtime[14:] in ['00:00', '30:00']:
            drop_list.append(dtime)
    df_x = df.drop(index=drop_list)
    return df_x

def go_trade(cci,ret):
    df_cci = pd.DataFrame({'datetime':list(cci.keys())})
    df_cci['cci'] = list(cci.values())
    df_cci = df_cci.set_index('datetime')
    df_ret = pd.concat([ret,df_cci], axis=1,sort=True)
    # df_ret = clean(df_ret)
    df_ret = df_ret.dropna()

    dtime = list(df_ret.index)
    ret_list = [1]
    for i in range(len(dtime)-1):
        k = dtime[i]
        # sym_list = list(set(df_ret.cci.loc[k]) & set(df_ret.rsrs.loc[k]))
        sym_list = list(set(df_ret.cci.loc[k]))
        if len(sym_list) != 0 :
            return_c = df_ret.iloc[i+1][sym_list].mean()
            ret_list.append(round(return_c,5))
        else:
            ret_list.append(0)
    df_ret['ret'] = ret_list
    df_ret['cret'] = df_ret.ret.cumsum()
    print('--Return data is ready...')
    return df_ret.cret


def calc_data(symbol_list,df,start,end):
    start_year = start
    end_year = end
    df_cci = copy.copy(df)
    df_ret = copy.copy(df)
    cret = pd.DataFrame()
    for sym in symbol_list:
    # 查询历史行情
        df_k = get_stk(sym, start_year, end_year)
        # df_k = get_k(sym, 60, 0, start_year, end_year)
        if len(df_k) == 0:
            continue
        df_k = df_k.set_index('datetime')
        df_k.loc[:, sym] = (df_k['close'] - df_k['close'].shift(1)) / df_k['close'].shift(1)
        cci_m = cci_calc(df_k, sym)
        df_cci = pd.concat([df_cci,cci_m],sort=True, axis=1).fillna(0)
        df_ret = pd.concat([df_ret, df_k[sym]], sort=True, axis=1).fillna(0)
        print('--' + sym + ' is loaded...')
    cci_signal = cci_filter(df_cci)
    print('--CCI signal is calculated...')
    cret_temp = go_trade(cci_signal, df_ret)
    cret = pd.concat([cret,cret_temp], sort=True,axis=1)
    return cret


s_time = '2015-01-01'
e_time = '2019-03-21'
total_return = []
return_m = []

# symbol_list = ['SHSE.603288']
symbol_list = ['SZSE.000002', 'SZSE.000333', 'SZSE.002456', 'SHSE.601318', 'SHSE.600585', 'SHSE.600660','SHSE.603288']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']
# symbol_list = ['SHSE.510050','SHSE.510500','SHSE.510880','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.518880'\
#     ,'SHSE.600036','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
#     ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
#     ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
#     ,'SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
#     ,'SZSE.002508','SZSE.002555','SZSE.002572','SZSE.002833','SZSE.159901','SZSE.159915','SZSE.159919']
# start_list = []
years = int(e_time[:4]) - int(s_time[:4]) + 1
start_year = s_time
end_year = e_time
symbol_idx = 'SHSE.000300'
index_data = get_k(symbol_idx, 60, 0, start_year, end_year)
df_idx = pd.DataFrame(index_data['datetime']).set_index('datetime')
df_idx = clean(df_idx)
print('--Index is loaded...')

cret = calc_data(symbol_list,df_idx,start_year,end_year)
print('--Program is done.')
cret.plot()



# ret = pd.DataFrame(total_return, columns=['symbol', 'start', 'end', 'return', 'mdd'])
# print(ret)

# filename = dt.now().strftime('%Y%m%d_%H%M%S') + '.csv'
# # t_r=pd.DataFrame(list(return_m))
# # t_r.to_csv(filename)
# t_s=pd.DataFrame(list(total_return))
# t_s.to_csv('R'+filename)

# statMatrx = pd.DataFrame()
# for sy in symbol_list:
#     for st in start_list:
#         queryStr = 'start==\'' + st + '\'&symbol==\'' + sy + '\''
#         test = ret.query(queryStr)
#         test['efc'] = (test['return']-1) / - test.mdd
#         test2 = test.groupby('f')
#         test3 =test2.mean()
#         test3.reset_index('f')
#         statMatrx=statMatrx.append(test3)
#
# statMatrx.to_csv('test_f.csv')
# test4 = statMatrx.groupby('f')
# test5 = test4.mean()
# test5.to_csv('calc_f.csv')