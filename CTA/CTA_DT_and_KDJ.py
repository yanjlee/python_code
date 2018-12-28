# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

# 结论：
# N: 3, fk_period = 9, sk and sd = 3 参数最优，超过80或者低于20反转的信号不强。

import pandas as pd
from ConnectDB import get_all_data
import os
import matplotlib.pyplot as plot
from decimal import Decimal
import numpy as np
import scipy as sp
from scipy.optimize import leastsq
import numpy as np
import talib as talib



def DT_KD(DT_N,K,KD_N,fk_period,sk_period,future):
    #实参数据定义##########################
    FEE = 3
    PRICE = 10

    fk_period = fk_period
    sk_period = sk_period
    kl = K
    ks = K

    EndTime_1 = '14:55'
    EndTime_2 = '23:00'



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

    # 获取数据, 创建DataFrame
    future_type = future
    items = 'datetime, open, high, low, close'
    table = 'fur_price_5m'
    condition = 'where symbol = \'' + future_type + '\' and datetime >= \'2018-08-20\' order by datetime asc'
    symbol_data = get_all_data(items, table, condition)
    df_price = pd.DataFrame(list(symbol_data), columns=['datetime','open','high','low','close'])
    df_price['chg'] = df_price['close'] -  df_price['close'].shift(1)
    df_price = df_price.fillna(0)
    df_price[['open','high','low','close']] = df_price[['open','high','low','close']].astype(float)
    # matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
    df_price['slow_k'], df_price['slow_d'] = talib.STOCH(df_price['high'].values,df_price['low'].values,df_price['close'].values,fastk_period=fk_period,slowk_period=sk_period,slowk_matype=1,slowd_period=sk_period,slowd_matype=1)
    # df_price['J'] = df_price.slow_k * 3 - 2 * df_price.slow_d
    df = df_price.dropna()


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
    high_HH = np.zeros(DT_N)
    close_HL = np.zeros(DT_N)
    low_LL = np.zeros(DT_N)
    k_avg = np.zeros(KD_N)
    d_avg = np.zeros(KD_N)
    open = 0

    signal = 0
    pre_pos = 0
    rt_list = []

    for i, row in enumerate(df.iterrows()):
        datetime = row[1][0]
        close = float(row[1][4])
        chg = row[1][5]
        k = row[1][6]
        d = row[1][7]

        high_HH[0:DT_N - 1] = high_HH[1:DT_N]
        close_HL[0:DT_N - 1]= close_HL[1:DT_N]
        low_LL[0:DT_N - 1] = low_LL[1:DT_N]

        high_HH[-1] = row[1][2]
        close_HL[-1] = row[1][4]
        low_LL[-1] = row[1][3]
        open = float(row[1][1])

        k_avg[0:KD_N - 1] = k_avg[1:KD_N]
        d_avg[0:KD_N - 1] = d_avg[1:KD_N]
        k_avg[-1] = k
        d_avg[-1] = d

        if i < DT_N - 1: # 跳过无数据记录
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        k_signal = k_avg.mean()
        d_signal = d_avg.mean()
        # if k_signal > d_signal and d_signal > 50:
        #     kl = 0.5
        # elif k_signal < d_signal and d_signal < 50:
        #     ks = 0.5
        if k_signal > d_signal and d_signal > 50:
            signal_1 = 1
        elif k_signal < d_signal and d_signal < 50:
            signal_1 = -1
        else:
            signal_1 = 0

        ranges = float(max(max(high_HH) - min(close_HL), max(close_HL) - min(low_LL)))
        open_up = open + kl * ranges
        open_down = open + ks * ranges
        if close > open_up and signal == 1:
            signal_2 = 1
        elif close < open_down  and signal == -1:
            signal_2 = -1
        else:
            signal_2 = 0

        if (signal_1 + signal_2) >= 1:
            signal = 1
        elif (signal_1 + signal_2) <= -1:
            signal = -1
        else:
            signal = 0

    ## 收市前清盘
        if (row[1][0].strftime('%H:%M') >= EndTime_1 and row[1][0].strftime('%H:%M') <= '15:00') or row[1][0].strftime('%H:%M') >= EndTime_2:
            signal = 0

    # 结果统计与展示
    df_rt = pd.DataFrame()
    # df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    # df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    # df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['net_pnl'] = [rt.net_pnl for rt in rt_list]
    df_rt['cum_pnl'] = df_rt['net_pnl'].cumsum().astype(float)
    max_draw_down = MaxDrawDown(df_rt['cum_pnl'] )
    df_rt['cum_pnl'].plot()
    # print([df_rt['cum_pnl'].iloc[-1], max_draw_down])

    return(df_rt['cum_pnl'].iloc[-1], max_draw_down)



total_return = []
future_list = ['TA1901','RU1901','M1901','J1901','J1905','RB1901','RB1905','RB1810','ZN1811','ZN1810','CU1811']
# future_list = ['J1901']
DT_N = 14
K = 1
KD_N = 3
fk_period = 9
sk_period = 3
for future in future_list:
    re, mdd = DT_KD(DT_N,K,KD_N,fk_period,sk_period,future)
    total_return.append([future,DT_N,K,KD_N,fk_period,sk_period,re,mdd])
    print(total_return[-1])

# filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
# t_r=pd.DataFrame(list(total_return))
# t_r.to_csv(filename)
# os.system('C:/codes/Blackberry.m4a')




# df_rt.to_csv('rt.csv')
# df_price.to_csv('price.csv')

