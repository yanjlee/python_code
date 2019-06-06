# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from ConnectDB import get_ft


def Run(df):
    #实参数据定义##########################
    FEE = 0
    PRICE = 10

    def MaxDrawDown(return_list):
        max_value = 0
        mdd = 0
        for i in return_list:
            max_value = max(i, max_value)
            if max_value != 0:
                mdd = min(mdd, round(i - max_value), 3)
            else:
                mdd = 0
        return(mdd)

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

        def trade_calc(self, datetime, close, chg, signal, pre_pos):
            self.datetime =datetime
            self.close = close
            self.chg = chg
            self.pos = signal
            self.pre_pos = pre_pos

            self.pnl = self.chg * self.pos * PRICE
            self.fee = abs(self.pos - self.pre_pos) * FEE
            self.net_pnl = self.pnl - self.fee


    # 策略和类初始化数据
    signal = 0
    pre_pos = 0
    rt_list = []
    # atr = df.atr.iloc[0]
    pre_close = df.close.iloc[0]
    pre_ama = df.close.iloc[0]
    max_price = 0
    buy_price = 0
    b_day = 0

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        # atr = row[1].atr
        # ma5 = row[1].ma5
        # ma34 = row[1].ma34
        ama = row[1].ama
        b_day = max(b_day - 1, 0)

        if i < 1: # 跳过无数据记录
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        if ama > pre_ama:
            signal = 1
        else:
            signal = -1

        # # ATR 止损
        # if signal == 1:
        #     max_price = max(max_price, row[1].high)
        # else:
        #     max_price = 0
        #
        # if close < (max_price - 2.2 * atr) and signal == 1:
        #     signal = 0
        # elif b_day != 0:
        #     signal = 0

        # # 百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # if b_day != 0:
        #     signal = 0
        # if pre_pos == 0 and signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_ama = ama

    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    df_rt['close'] = [rt.close for rt in rt_list]
    df_rt['chg'] = [rt.chg for rt in rt_list]
    df_rt['pos'] = [rt.pos for rt in rt_list]
    df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['net_pnl'] = [rt.net_pnl for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['net_pnl'].cumsum().astype(float) + 1, 2)
    df_rt['raw_cret'] = round((df_rt['chg'] * PRICE).cumsum().astype(float) + 1, 2)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    df_rt.to_csv('test.csv')
    return (df_rt.cum_rate.iloc[-1], max_draw_down, df_rt[['cum_rate', 'raw_cret']])


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

    # ax3.plot(date_strings, k_data['ii'], color='red', label='II%')
    # ax3.plot(date_strings, k_data['ad%'], color='green', label='AD%')
    # ax3.plot(date_strings, k_data['mfi'] / 100 - 0.5, color='blue', label='MFI')
    # ax3.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    # ax3.axhline(0.15, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    # ax3.legend(loc='upper left', frameon=False)
    #
    # ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    # ax2.plot(date_strings, k_data['bp'] * 100, color='red', label='bp%')
    # # ax2.plot(date_strings, k_data['mfi'], color='blue', label='mfi')
    # # ax2.plot(date_strings, k_data['cci'], color='blue', label='cci')
    # ax2.legend(loc='upper left', frameon=False)
    #
    # ax2t.set_ylim(float(min(k_data.cci)), float(max(k_data.cci)))
    # ax2t.plot(date_strings, k_data['cci'], color='green', label='cci')
    # ax2t.legend(loc='upper right', frameon=False)
    # ax2t.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    # ax2t.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    # ax2t.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    ax.plot(date_strings, k_data['mid'], color='m', label='mid')
    ax.plot(date_strings, k_data['up2'], color='blue', label='up2')
    ax.plot(date_strings, k_data['dn2'], color='brown', label='dn2')
    ax.plot(date_strings, k_data['up1'], color='green', label='up1')
    ax.plot(date_strings, k_data['dn1'], color='olive', label='dn1')
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

def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)


def ta_bbands(data, n=20):
    df = pd.DataFrame()
    df['up2'], df['mid'], df['dn2'] = ta.BBANDS(data.values, timeperiod=n,nbdevup=2,nbdevdn=2,matype=0)
    df['up1'], df['mid1'], df['dn1'] = ta.BBANDS(data.values, timeperiod=n, nbdevup=1, nbdevdn=1, matype=0)
    df =  df.drop(columns = ['mid1']).round(2)
    return df

n = 20
atr_n = 20
start_time = '2019-01-01'
end_time = '2019-04-30'
total_return = []

# future_list = ['PP0','TA0','V0','EG0','ZC0','SC0','L0','WH0','RI0','LR0','CY0','CF0','P0','RU0','BU0','PB0','CU0','AL0','ZN0','SN0','NI0','HC0','J0','JM0','FU0','CS0','C0','FG0','SR0','AG0','SF0','JR0','FB0','SP0','WR0','BB0','OI0','RS0','RM0','RB0','A0','B0','Y0','M0','MA0','I0','SM0','AP0','JD0','AU0']
future_list = ['J0','RB0','I0','M0','TA0','NI0','AL0']
# future_list = ['J0']

for symbol in future_list:
    df_data = get_ft(symbol, start_time, end_time)
    if len(df_data) == 0:
        continue
    df_data.loc[:,'ace'] = 0.191 * (df_data.high + df_data.low) + 0.236 * df_data.open + df_data.close * 0.382
    df_data.loc[:, 'ama'] = df_data.ace#.rolling(8,min_periods=0).mean()
    # df_data.loc[:, 'ma5'] = df_data.close.rolling(5,min_periods=0).mean()
    # df_data.loc[:, 'ma34'] = df_data.close.rolling(34,min_periods=0).mean()
    # df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
    # cci_n = [5, 10, 20]
    # cci_len = len(cci_n)
    # cci_m = pd.DataFrame()
    # for n in cci_n:
    #     cci_m = pd.concat([cci_m, ta_cci(n, df_data[['high','low','close']])], axis=1)

    # df_data = pd.concat([df_data, ta_bbands(df_data.ace,n)], axis=1)
    df_data.loc[:, 'chg'] = df_data['close'] - df_data['close'].shift(1)
    df_data = df_data.dropna()
    # print(df_data)
    # print(df_data.columns)
    # DrawSignals(df_data)

    re, mdd, df_k = Run(df_data)
    total_return.append([symbol, re, mdd])
    #
    # print(total_return[-1])
    ax = df_k.plot(title=symbol)
    fig = ax.get_figure()
    # fig.savefig(symbol + '_kdj' + '.png')
    # plt.close(fig)