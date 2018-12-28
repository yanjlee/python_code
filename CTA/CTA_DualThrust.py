# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

# 结论：
# K-- 0.6及以上过滤震荡效果比较好，N--6及以上效果比较稳定。K>1, N>10以上结果开始稳定

from datetime import timedelta, datetime
import pandas as pd
from ConnectDB import get_all_data
import os
import matplotlib.pyplot as plot
from decimal import Decimal
import numpy as np
import scipy as sp
from scipy.optimize import leastsq
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import statsmodels.api as sm

def DualThrust(N,K,future):
    #实参数据定义##########################
    FEE = 3
    PRICE = 10
    N = N
    kl = K
    ks = K
    EndTime_1 = '14:55'
    EndTime_2 = '23:00'


    # 获取数据, 创建DataFrame
    future_type = future
    items = 'datetime, open, high, low, close'
    table = 'fur_price_5m'
    condition = 'where symbol = \'' + future_type + '\' and datetime >= \'2018-08-20\' order by datetime asc'
    symbol_data = get_all_data(items, table, condition)
    df_price = pd.DataFrame(list(symbol_data), columns=['datetime','open','high','low','close'])
    df_price['chg'] = df_price['close'] -  df_price['close'].shift(1)
    df_price = df_price.fillna(0)

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
    high_HH = np.zeros(N)
    close_HL = np.zeros(N)
    low_LL = np.zeros(N)
    open = 0

    signal = 0
    pre_pos = 0
    rt_list = []

    for i, row in enumerate(df_price.iterrows()):
        datetime = row[1][0]
        close = float(row[1][4])
        chg = row[1][5]

        high_HH[0:N-1] = high_HH[1:N]
        close_HL[0:N-1]= close_HL[1:N]
        low_LL[0:N-1] = low_LL[1:N]

        high_HH[-1] = row[1][2]
        close_HL[-1] = row[1][4]
        low_LL[-1] = row[1][3]
        open = float(row[1][1])


        if i < N - 1: # 跳过无数据记录
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        ranges = float(max(max(high_HH) - min(close_HL), max(close_HL) - min(low_LL)))
        open_up = open + kl * ranges
        open_down = open + ks * ranges
        if close > open_up:
            signal = 1
        elif close < open_down:
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

    return(df_rt['cum_pnl'][i-N-1], max_draw_down)

def MaxDrawDown(return_list):
    max_value = 0
    mdd = 0
    for i in return_list:
        max_value = max(i, max_value)
        if max_value != 0:
            mdd = min(0, round(i - max_value), 3)
        else:
            mdd = 0
    return(mdd)

# total_return = []
# future_list = ['TA1901']
# for future in future_list:
#     for N in range(5,22):
#         for k in range(5,22):
#             K = k/10
#             re, mdd = DualThrust(N,K,future)
#             total_return.append([future,N,K,re,mdd])
#             print(total_return[-1])

# filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
# t_r=pd.DataFrame(list(total_return))
# t_r.to_csv(filename)
# os.system('C:/codes/Blackberry.m4a')

N = 14
K = 1
future = 'ZN1811'
re, mdd = DualThrust(N, K, future)
print([future, N, K, re, mdd])



# df_rt.to_csv('rt.csv')
# df_price.to_csv('price.csv')


## MaxDrawdown
## SharpRatio
## KDJ
