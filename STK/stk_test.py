# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta, datetime as dt
import talib as ta
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import numpy as np
from STK.tsdata import get_k_stk as get_k


# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

def Run(ma_list, cci_n, k_data):
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
    k_data['chg'] = (k_data['close'] - k_data['close'].shift(1))/ k_data['close'].shift(1)
    df = k_data.dropna()

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

    cci_col = []
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(df[cci_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[1].datetime
        close = row[1].close
        chg = row[1].chg
        cci_list = list(row[1][cci_col])

        ma5 = row[1].ma5
        ma10 = row[1].ma10
        ma20 = row[1].ma20

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos


    ## 策略信号
        signal_list =[]

        ## MA 策略
        if close > ma20:

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

        signal_value = sum(signal_list) # 计算产生总信号
        if signal_value > 0:
            signal = 1
        elif signal_value < 0:
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

        # 百分比止损
        stop_loss = 0.05
        if signal == 1 and close < buy_price * (1 - stop_loss):
            signal = 0
        if pre_pos == 0 and signal == 1:
            buy_price = pre_close
        elif pre_pos == 1 and signal == 0:
            buy_price = 0

        ## 保留前一天close数据
        pre_close = close

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

#Moving Average
def MA(df, n):
    ma = pd.Series(ta.MA(df.close,n), name = 'ma' + str(n))
    df = df.join(ma)
    return(df)


#Exponential Moving Average
def EMA(df, n):
    ema = pd.Series(ta.EMA(df.close,n), name = 'ema' + str(n))
    df = df.join(ema)
    return df

def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))


s_time = '2014-01-01'
e_time = '2018-12-31'
total_return = []
return_m = []
symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600660','SHSE.603288']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']
# symbol_list = ['SHSE.603288']
start_list = []

for n_year in range(0, 5):
    start_year = dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * n_year
    end_year = dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * (n_year+1)
    start_list.append(start_year.strftime('%Y-%m-%d'))
    start_year = start_year.strftime('%Y-%m-%d')
    end_year = end_year.strftime('%Y-%m-%d')

    # start_year = s_time
    # end_year = e_time

    for sym in symbol_list:
    # 查询历史行情
    #     df_k = history(symbol=sym, frequency='1h', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
        df_k = get_k(sym, 60, 0, start_year, end_year)
        if len(df_k) == 0:
            continue

        ma_list = [5, 10, 20]
        for n in ma_list:
            df_k = MA(df_k, n)

        cci_n = [15, 30, 60]
        cci_m = pd.DataFrame()
        for n in cci_n:
            cci_m = pd.concat([cci_m, ta_cci(n, df_k)], axis=1)

        k_data = pd.concat([df_k, ta_atr(30, df_k), cci_m], axis=1)
        k_data.rename(columns={'eob': 'datetime'}, inplace=True)

        # k_data = k_data.dropna()
        # DrawSignals(k_data)

        re, mdd, df_r = Run(ma_list, cci_n, k_data)
        # k_data = k_data.set_index('datetime')
        # k_data = pd.concat([k_data,df_r], axis=1)
        # k_data = k_data.reset_index('datetime')
        # DrawSignals2(k_data)
        print([sym, start_year, end_year, re, mdd])
        # print(str(k_data.datetime.iloc[0]) + ' ~ ' + str(k_data.datetime.iloc[-1]))
        total_return.append([sym, start_year, end_year, re, mdd])

ret = pd.DataFrame(total_return, columns=['symbol', 'start', 'end', 'return', 'mdd'])


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