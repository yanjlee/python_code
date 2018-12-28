# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

# 结论：
# 双均线、指数均线等策略在成熟期货交易上已跟不上市场，人为的震荡行情会使得盈利耗费殆尽，不可能盈利。同时也可以说，简单的双均线策略缺乏
# 对震荡的过滤，缺乏止损，策略效果很差

from datetime import timedelta, datetime
import pandas as pd
from ConnectDB import get_all_data
import matplotlib.pyplot as plot
from decimal import Decimal
import numpy as np
import scipy as sp
from scipy.optimize import leastsq
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import statsmodels.api as sm

#实参数据定义##########################
FEE = 3
PRICE = 10
Short = 5
Long = 20
EndTime_1 = '14:55'
EndTime_2 = '23:00'


# 获取数据, 创建DataFrame
future_type = 'rb1901'
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
close_sdays = np.zeros(Short)
close_ldays = np.zeros(Long)
signal = 0
pre_pos = 0
rt_list = []

for i, row in enumerate(df_price.iterrows()):
    datetime = row[1][0]
    close = row[1][4]
    chg = row[1][5]

    close_sdays[0:Short-1] = close_sdays[1:Short]
    close_ldays[0:Long-1] = close_ldays[1:Long]
    close_sdays[-1], close_ldays[-1] = close, close

    if i < Long - 1: # 跳过无数据记录
        continue

## 数据与信号驱动计算
    rt = ActStatus()
    rt.trade_calc(datetime, close, chg, signal, pre_pos)
    rt_list.append(rt)
    pre_pos = rt.pos

## 策略信号
    ma_short = close_sdays.mean()
    ma_long = close_ldays.mean()
    if ma_short >= ma_long:
        signal = 1
    else:
        signal = -1

## 收市前清盘
    if row[1][0].strftime('%H:%M') == EndTime_1 or row[1][0].strftime('%H:%M') == EndTime_2:
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
df_rt['cum_pnl'].plot()

# df_rt.to_csv('rt.csv')
# df_price.to_csv('price.csv')

# def two_ma(df_price, short, long):
#     df = df_price.copy()
#     df['chg'] = df['close'] - df['close'].shift(1)
#     df['ma' + str(short)] = df['close'].rolling(window=short, center=False).mean()
#     df['ma' + str(long)] = df['close'].rolling(window=long, center=False).mean()
#
#
#     df['pos'] = 0
#     pos = list(df['ma' + str(short)] >= df['ma' + str(long)])
#     pos = [1 if x is True else -1 for x in pos]
#     df['pos'] = pd.DataFrame(pos)
#     df['pos'] =  df['pos'].shift(1).fillna(0)
#     df = df.dropna()
#
#     # df['pnl'] = df['chg'] * df['pos'] # 股票持仓的计算方法，chg列的计算也要更改
#     df['pnl'] = df['chg'] * 10* df['pos'] # 期货持有多空的计算方法
#     df['fee'] = 0
#     df['fee'][df['pos'] != df['pos'].shift(1)] = df['close'] / 0.15*0.0001
#     df['netpnl'] = df['pnl'] - df['fee']
#     df['cumpnl'] = df['netpnl'].cumsum()
#     return(df)
#
#
# df = two_ma(df_price, 5,20)
# for i, row in enumerate(df.iterrows()):
#     print(i)
#     print(row)
# # df['cumpnl'].plot()
#
# def two_ema(short, long):
#     df_price['ema5'] = df_price['close'].ewm(span=short, min_periods=0, adjust=True,ignore_na=False).mean()
#     df_price['ema5_2'] = df_price['ema5'].ewm(span=short, min_periods=0, adjust=True,ignore_na=False).mean()
#     df_price['ema21'] = df_price['close'].ewm(span=long, min_periods=0, adjust=True,ignore_na=False).mean()
#     # df_price['margin'] = df_price['ace']-df_price['ema5']
#
#     operation_list = [0]
#     operation_list_2 = [0]
#     return_list = [0]
#     return_list_2 = [0]
#
#     for j in range(0, len(df_price)-1):
#         if df_price['ema5'][j] >  df_price['ema21'][j]:
#             operation_list.append(1)
#             return_list.append(df_price['close'][j+1] - df_price['close'][j])
#         else:
#             operation_list.append(-1)
#             return_list.append(df_price['close'][j] - df_price['close'][j+1])
#
#         if df_price['ema5_2'][j] > df_price['ema21'][j]:
#             operation_list_2.append(1)
#             return_list_2.append(df_price['close'][j+1] - df_price['close'][j])
#         else:
#             operation_list_2.append(-1)
#             return_list_2.append(df_price['close'][j] - df_price['close'][j+1])
#
#     r1 = sum(return_list)
#     r2 = sum(return_list_2)
#     return(r1, r2)


# return_matrix = []
# for n in range(1,14):
#     for m in range(2,36):
#         if n>=m:
#             continue
#         else:
#             r1, r2 = two_ema(n,m)
#             return_matrix.append([n,m,r1,r2])
# df = pd.DataFrame(return_matrix)

# df_trade = pd.DataFrame(operation_list, columns=['t_1'])
# df_trade['t_2'] = pd.DataFrame(operation_list_2)
# df_trade['r_1'] = pd.DataFrame(return_list)
# df_trade['r_2'] = pd.DataFrame(return_list_2)

# df = pd.concat([df_price,df_trade],axis = 1)

# # 计算OLS，取斜率
# # results = sm.OLS(y,x).fit()
# # results.params.item()
# x_ray = [1,2,3,5,8]
# margin_list = list(df_price['margin'])
# ols_beta = []
# for j in range(0, len(margin_list)-4):
#     temp = []
#     for k in range(0,5):
#         temp.append(margin_list[j+k])
#     y_ray = temp
#     ols_result = sm.OLS(y_ray, x_ray).fit()
#     ols_beta.append(round(ols_result.params.item(),3))
#
# beta = [0,0,0,0] + ols_beta
# df_price['beta'] = pd.DataFrame(beta)
# df_price['angle'] = np.arctan(df_price['beta'])*180/PI

# filename = datetime.now().strftime('%Y%m%d%H%M%S_') + future_type + '.csv'
# df.to_csv(filename)

# beta指数5日平滑

# 排除夜班交易时间数据

# 日内交易，下午15：00清盘

# 历史波动率