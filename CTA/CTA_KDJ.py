# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

import pandas as pd
import numpy as np
import talib as ta
from ConnectDB import get_ft


def Run(df):
    #实参数据定义##########################
    FEE = 2.5
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

    for i, row in enumerate(df.iterrows()):
        datetime = row[1][0]
        close = float(row[1][4])
        chg = row[1][5]
        k = row[1][6]
        d = row[1][7]

        if i < 1: # 跳过无数据记录
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        if k > d:# and pre_k < pre_d:
            signal = 1
        elif k < d:# and pre_k > pre_d:
            signal = -1
        else:
            signal = 0

    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    df_rt['close'] = [rt.close for rt in rt_list]
    df_rt['chg'] = [rt.chg for rt in rt_list]
    df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['net_pnl'] = [rt.net_pnl for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['net_pnl'].cumsum().astype(float) + 1, 2)
    df_rt['raw_cret'] = round((df_rt['chg'] * PRICE).cumsum().astype(float) + 1, 2)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    df_rt.to_csv('test.csv')
    return (df_rt.cum_rate.iloc[-1], max_draw_down, df_rt[['cum_rate', 'raw_cret']])


def ta_kdj(data, fastk_period=9, slowk_period=3, slowd_period=3):
    indicators={}
    #计算kd指标
    high_prices = np.array(data['high'])
    low_prices = np.array(data['low'])
    close_prices = np.array(data['close'])
    indicators['k'], indicators['d'] = ta.STOCH(high_prices, low_prices, close_prices,fastk_period=fastk_period,\
                                                slowk_period=slowk_period, slowk_matype = 1,\
                                                slowd_period=slowd_period, slowd_matype = 1)
    # matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
    kdj = pd.DataFrame(indicators).round(2)
    return kdj


start_time = '2018-01-01'
end_time = '2019-04-30'
total_return = []

# future_list = ['PP0','TA0','V0','EG0','ZC0','SC0','L0','WH0','RI0','LR0','CY0','CF0','P0','RU0','BU0','PB0','CU0','AL0','ZN0','SN0','NI0','HC0','J0','JM0','FU0','CS0','C0','FG0','SR0','AG0','SF0','JR0','FB0','SP0','WR0','BB0','OI0','RS0','RM0','RB0','A0','B0','Y0','M0','MA0','I0','SM0','AP0','JD0','AU0']
future_list = ['J0','RB0','I0','M0','TA0','NI0','AL0']

for symbol in future_list:
    df_data = get_ft(symbol, start_time, end_time)
    if len(df_data) == 0:
        continue
    #     # df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
    df_data.loc[:, 'chg'] = df_data['close'] - df_data['close'].shift(1)
    df_data = pd.concat([df_data, ta_kdj(df_data)], axis=1)
    df_data = df_data.dropna()
    re, mdd, df_k = Run(df_data)
    total_return.append([symbol, re, mdd])

    # df_data.loc[:, 'ma5'] = df_data.close.rolling(3, min_periods=0).mean()
    # df_data.loc[:, 'ma34'] = df_data.close.rolling(13, min_periods=0).mean()


    # print(df_data)
    ax = df_k.plot(title=symbol)
    fig = ax.get_figure()
    # fig.savefig(symbol + '_kdj' + '.png')
    # plt.close(fig)