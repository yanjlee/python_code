# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

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

# PI = 3.1415926

# 获取数据
future_type = 'rb1901'
items = 'datetime, open, high, low, close'
table = 'fur_price_5m'
condition = 'where symbol = \'' + future_type + '\' and datetime >= \'2018-08-20\' order by datetime asc'
symbol_data = get_all_data(items, table, condition)

# 标准化数据
x_list = []
y_list = []
close_list = []
open_list = []

for i in range(0, len(symbol_data)):
    x_list.append(symbol_data[i][0].strftime('%Y-%m-%d %H:%M'))
    close_list.append(float(symbol_data[i][4]))
    open_list.append(float(symbol_data[i][1]))
    # ace = Decimal('0.1') * (symbol_data[i][2] + symbol_data[i][3]) + Decimal('0.3') * symbol_data[i][1] + Decimal('0.5') * symbol_data[i][4]
    # y_list.append(float(ace))


# 创建DataFrame
df_price = pd.DataFrame(x_list, columns=['datetime'])
df_price['open'] = pd.DataFrame(open_list)
df_price['close'] = pd.DataFrame(close_list)
# df_price['ace'] = pd.DataFrame(y_list)

def two_ma(df_price, short, long):
    df = df_price.copy()
    df['chg'] = df['close'] - df['close'].shift(1)
    df['ma' + str(short)] = df['close'].rolling(window=short, center=False).mean()
    df['ma' + str(long)] = df['close'].rolling(window=long, center=False).mean()


    df['pos'] = 0
    pos = list(df['ma' + str(short)] >= df['ma' + str(long)])
    pos = [1 if x is True else -1 for x in pos]
    df['pos'] = pd.DataFrame(pos)
    df['pos'] =  df['pos'].shift(1).fillna(0)
    df = df.dropna()

    # df['pnl'] = df['chg'] * df['pos'] # 股票持仓的计算方法，chg列的计算也要更改
    df['pnl'] = df['chg'] * 10* df['pos'] # 期货持有多空的计算方法
    df['fee'] = 0
    df['fee'][df['pos'] != df['pos'].shift(1)] = df['close'] / 0.15*0.0001
    df['netpnl'] = df['pnl'] - df['fee']
    df['cumpnl'] = df['netpnl'].cumsum()
    return(df)


df = two_ma(df_price, 5,20)
for i, row in enumerate(df.iterrows()):
    print(i)
    print(row)
# df['cumpnl'].plot()

def two_ema(short, long):
    df_price['ema5'] = df_price['close'].ewm(span=short, min_periods=0, adjust=True,ignore_na=False).mean()
    df_price['ema5_2'] = df_price['ema5'].ewm(span=short, min_periods=0, adjust=True,ignore_na=False).mean()
    df_price['ema21'] = df_price['close'].ewm(span=long, min_periods=0, adjust=True,ignore_na=False).mean()
    # df_price['margin'] = df_price['ace']-df_price['ema5']

    operation_list = [0]
    operation_list_2 = [0]
    return_list = [0]
    return_list_2 = [0]

    for j in range(0, len(df_price)-1):
        if df_price['ema5'][j] >  df_price['ema21'][j]:
            operation_list.append(1)
            return_list.append(df_price['close'][j+1] - df_price['close'][j])
        else:
            operation_list.append(-1)
            return_list.append(df_price['close'][j] - df_price['close'][j+1])

        if df_price['ema5_2'][j] > df_price['ema21'][j]:
            operation_list_2.append(1)
            return_list_2.append(df_price['close'][j+1] - df_price['close'][j])
        else:
            operation_list_2.append(-1)
            return_list_2.append(df_price['close'][j] - df_price['close'][j+1])

    r1 = sum(return_list)
    r2 = sum(return_list_2)
    return(r1, r2)


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