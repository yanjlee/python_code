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
from STK.tsdata import get_k_stk as get_k, get_stk
import statsmodels.api as sm # 最小二乘
import copy
#from statsmodels.stats.outliers_influence import summary_table # 获得汇总信息
#from sklearn.preprocessing import MinMaxScaler, StandardScaler



# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

def Run(dataset):
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
    df = dataset.set_index('datetime')

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
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        ma5 = row[1].ma5
        ma34 = row[1].ma34
        b_day = max(b_day - 1, 0)
        # cci_list = list(row[1][cci_col])

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        if ma5 > ma34:
            signal = 1
        elif ma5 < ma34:
            signal = 0
        else:
            signal = pre_pos

        # ##ATR 止损
        # if signal == 1:
        #     max_price = max(max_price, row[1].high)
        # else:
        #     max_price = 0
        #
        # if close < (max_price - 2.2 * atr) and signal == 1:
        #     signal = 0
        # elif b_day != 0:
        #     signal = 0

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
    df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    ax = df_rt[['cum_rate', 'raw_cret']].plot(title= sym )
    fig = ax.get_figure()
    fig.savefig(sym + '_ma.png')
    df_rt = df_rt.set_index('datetime')
    return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)


def DrawSignals(k_data):
    # 作图
    stick_freq = 50 # 横坐标间隔

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

    # ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    # ax2.plot(date_strings, k_data['zs']*100, color='red', label='zs')
    # ax2.axhline(80, linestyle='dotted', color='m', lw=0.5)  ## 画一条水平收益基准线
    # ax2.axhline(-80, linestyle='dotted', color='b', lw=0.5)  ## 画一条水平收益基准线
    # ax2.legend(loc='upper left', frameon=False)

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())
    ax.plot(date_strings, k_data['ma5'], color='m', label='ma5')
    ax.plot(date_strings, k_data['ma20'], color='blue', label='ma20')
    ax.plot(date_strings, k_data['ma60'], color='green',label='ma60')
    ax.plot(date_strings, k_data['ma120'],color='red', label='ma120')
    ax.legend(loc='upper left', frameon=False)

    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化
    # ax2.grid(True, linestyle='dotted', linewidth='0.5')

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


def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))

#Moving Average
def MA(df, n):
    MA = pd.Series(pd.rolling_mean(df['Close'], n), name = 'MA_' + str(n))
    df = df.join(MA)
    return df

#Exponential Moving Average
def EMA(df, n):
    EMA = pd.Series(pd.ewma(df['Close'], span = n, min_periods = n - 1), name = 'EMA_' + str(n))
    df = df.join(EMA)
    return df


def clean(df):
    drop_list = []
    for dtime in list(df.index):
        if dtime[14:] not in ['00:00', '30:00']:
        # if dtime[14:] in ['00:00', '30:00']:
            drop_list.append(dtime)
    df_x = df.drop(index=drop_list)
    return df_x

def ma_filter(df):
    ma_dict={}
    for i, row in enumerate(df.iterrows()):
        ma_dict[row[0]] = list(row[1][row[1] == True].index)
    return ma_dict

def go_trade(ma,ret):
    df_ma2 = pd.DataFrame({'datetime':list(ma.keys())})
    df_ma2['ma'] = list(ma.values())
    df_ma2 = df_ma2.set_index('datetime')
    df_ret = pd.concat([ret,df_ma2], axis=1,sort=True)
    # df_ret = clean(df_ret)
    df_ret = df_ret.dropna()

    dtime = list(df_ret.index)
    ret_list = [1]
    for i in range(len(dtime)-1):
        k = dtime[i]
        # sym_list = list(set(df_ret.cci.loc[k]) & set(df_ret.rsrs.loc[k]))
        sym_list = list(set(df_ret.ma.loc[k]))
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
    df_ma = copy.copy(df)
    df_ret = copy.copy(df)
    cret = pd.DataFrame()
    for sym in symbol_list:
    # 查询历史行情
    #     df_k = get_stk(sym, start_year, end_year)
        df_k = get_k(sym, 60, 0, start_year, end_year)
        if len(df_k) == 0:
            continue
        df_k = df_k.set_index('datetime')
        df_k.loc[:, sym] = (df_k['close'] - df_k['close'].shift(1)) / df_k['close'].shift(1)
        for ma_n in [5,34]:#[3,5,20,34,60,120]:
            # df_data.loc[:, 'ace'] = df_data['close'] * 0.382 + 0.206 *(df_data['high'] + df_data['low'] + df_data['open'])
            df_k.loc[:,'ma'+str(ma_n)] = df_k.close.rolling(ma_n,min_periods=0).mean()
        df_ma.loc[:,sym] = df_k.ma5 > df_k.ma34
        df_ret = pd.concat([df_ret, df_k[sym]], sort=True, axis=1).fillna(0)
        print('--' + sym + ' is loaded...')

    ma_signal = ma_filter(df_ma)
    print('--MA signal is calculated...')
    cret_temp = go_trade(ma_signal, df_ret)
    cret = pd.concat([cret,cret_temp], sort=True,axis=1)
    return cret,ma_signal
    # return df_ma


s_time = '2018-01-01'
e_time = '2019-03-21'
total_return = []
return_m = []
# symbol_list = ['SZSE.002456','SHSE.600036']
symbol_list = ['SHSE.600036','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
    ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
    ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
    ,'SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
    ,'SZSE.002508','SZSE.002555','SZSE.002572','SZSE.002833']

# symbol_list = ['SHSE.510050','SHSE.510500','SHSE.510880','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.518880'\
#     ,'SHSE.600036','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
#     ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
#     ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
#     ,'SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
#     ,'SZSE.002508','SZSE.002555','SZSE.002572','SZSE.002833','SZSE.159901','SZSE.159915','SZSE.159919']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']

years = int(e_time[:4]) - int(s_time[:4]) + 1
start_year = s_time
end_year = e_time

symbol_idx = 'SHSE.000300'
index_data = get_k(symbol_idx, 60, 0, start_year, end_year)
df_idx = pd.DataFrame(index_data['datetime']).set_index('datetime')
df_idx = clean(df_idx)
print('--Index is loaded...')

cret,ma_signal = calc_data(symbol_list,df_idx,start_year,end_year)
# cret = go_trade(cci_signal,rsrs_signal,df_ret)
print('--Program is done.')
cret.plot()

