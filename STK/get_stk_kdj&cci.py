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
from STK.tsdata import get_k_stk as get_k, get_stk, get_stk_1h
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
    pre_k = 50
    pre_d = 50

    cci_col = []
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(df[cci_col].iloc[0])
    kdj_col = []
    for kd in kdj_n:
        kdj_col.append('k' + str(kd))
        kdj_col.append('d' + str(kd))
    pre_kdj_list = list(df[kdj_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        # b_day = max(b_day - 1, 0)
        cci_list = list(row[1][cci_col])
        kdj_list = list(row[1][kdj_col])

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号

        ## CCI策略
        signal_cci_list = []
        for j in range(0, len(cci_n)):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            ci = 101
            range_value = 50
            for i in range(-ci, ci + 300, range_value):
                if pre_cci < i and cci > i:
                    signal_cci_list.append(1)
                elif pre_cci > i and cci < i:
                    signal_cci_list.append(-1)
                else:
                    signal_cci_list.append(0)
        signal_cci_value = sum(signal_cci_list)  # 计算产生总信号



        ## KDJ策略
        signal_kdj_list = []
        for j in range(0, len(kdj_n)*2,2):
            pre_k = pre_kdj_list[j]
            pre_d = pre_kdj_list[j+1]
            k = kdj_list[j]
            d = kdj_list[j+1]
            if k > d and pre_k < pre_d:
                signal_kdj_list.append(1)
            elif k < d and pre_k > pre_d:
                signal_kdj_list.append(-1)
            else:
                signal_kdj_list.append(0)
        signal_kdj_value = sum(signal_cci_list)

        if signal_cci_value > 0 or signal_kdj_value > 0:
            signal = 1
        elif signal_cci_value < 0 and signal_kdj_value < 0:
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
        # # elif b_day != 0:
        # #     signal = 0
        # #
        # ##百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # # if b_day != 0:
        # #     signal = 0
        #
        # if pre_pos == 0 or signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     # b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_kdj_list = kdj_list
        pre_cci_list = cci_list


    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    ax = df_rt[['cum_rate', 'raw_cret']].plot(title= sym )
    fig = ax.get_figure()
    fig.savefig(sym + '_cci&kdj_or_and.png')
    df_rt = df_rt.set_index('datetime')
    plt.close(fig)
    # df_rt.to_csv('test.csv')
    return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)

def Run_aa(dataset):
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
    pre_k = 50
    pre_d = 50

    cci_col = []
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(df[cci_col].iloc[0])
    kdj_col = []
    for kd in kdj_n:
        kdj_col.append('k' + str(kd))
        kdj_col.append('d' + str(kd))
    pre_kdj_list = list(df[kdj_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        # b_day = max(b_day - 1, 0)
        cci_list = list(row[1][cci_col])
        kdj_list = list(row[1][kdj_col])

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号

        ## CCI策略
        signal_cci_list = []
        for j in range(0, len(cci_n)):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            ci = 101
            range_value = 50
            for i in range(-ci, ci + 300, range_value):
                if pre_cci < i and cci > i:
                    signal_cci_list.append(1)
                elif pre_cci > i and cci < i:
                    signal_cci_list.append(-1)
                else:
                    signal_cci_list.append(0)
        signal_cci_value = sum(signal_cci_list)  # 计算产生总信号



        ## KDJ策略
        signal_kdj_list = []
        for j in range(0, len(kdj_n)*2,2):
            pre_k = pre_kdj_list[j]
            pre_d = pre_kdj_list[j+1]
            k = kdj_list[j]
            d = kdj_list[j+1]
            if k > d and pre_k < pre_d:
                signal_kdj_list.append(1)
            elif k < d and pre_k > pre_d:
                signal_kdj_list.append(-1)
            else:
                signal_kdj_list.append(0)
        signal_kdj_value = sum(signal_cci_list)

        if signal_cci_value > 0 and signal_kdj_value > 0:
            signal = 1
        elif signal_cci_value < 0 and signal_kdj_value < 0:
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
        # # elif b_day != 0:
        # #     signal = 0
        # #
        # ##百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # # if b_day != 0:
        # #     signal = 0
        #
        # if pre_pos == 0 or signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     # b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_kdj_list = kdj_list
        pre_cci_list = cci_list


    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    ax = df_rt[['cum_rate', 'raw_cret']].plot(title= sym )
    fig = ax.get_figure()
    fig.savefig(sym + '_cci&kdj_and_and.png')
    df_rt = df_rt.set_index('datetime')
    plt.close(fig)
    # df_rt.to_csv('test.csv')
    # return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)

def Run_ao(dataset):
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
    pre_k = 50
    pre_d = 50

    cci_col = []
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(df[cci_col].iloc[0])
    kdj_col = []
    for kd in kdj_n:
        kdj_col.append('k' + str(kd))
        kdj_col.append('d' + str(kd))
    pre_kdj_list = list(df[kdj_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        # b_day = max(b_day - 1, 0)
        cci_list = list(row[1][cci_col])
        kdj_list = list(row[1][kdj_col])

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号

        ## CCI策略
        signal_cci_list = []
        for j in range(0, len(cci_n)):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            ci = 101
            range_value = 50
            for i in range(-ci, ci + 300, range_value):
                if pre_cci < i and cci > i:
                    signal_cci_list.append(1)
                elif pre_cci > i and cci < i:
                    signal_cci_list.append(-1)
                else:
                    signal_cci_list.append(0)
        signal_cci_value = sum(signal_cci_list)  # 计算产生总信号



        ## KDJ策略
        signal_kdj_list = []
        for j in range(0, len(kdj_n)*2,2):
            pre_k = pre_kdj_list[j]
            pre_d = pre_kdj_list[j+1]
            k = kdj_list[j]
            d = kdj_list[j+1]
            if k > d and pre_k < pre_d:
                signal_kdj_list.append(1)
            elif k < d and pre_k > pre_d:
                signal_kdj_list.append(-1)
            else:
                signal_kdj_list.append(0)
        signal_kdj_value = sum(signal_cci_list)

        if signal_cci_value > 0 and signal_kdj_value > 0:
            signal = 1
        elif signal_cci_value < 0 or signal_kdj_value < 0:
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
        # # elif b_day != 0:
        # #     signal = 0
        # #
        # ##百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # # if b_day != 0:
        # #     signal = 0
        #
        # if pre_pos == 0 or signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     # b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_kdj_list = kdj_list
        pre_cci_list = cci_list


    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    ax = df_rt[['cum_rate', 'raw_cret']].plot(title= sym )
    fig = ax.get_figure()
    fig.savefig(sym + '_cci&kdj_and_or.png')
    df_rt = df_rt.set_index('datetime')
    plt.close(fig)
    # df_rt.to_csv('test.csv')
    # return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)



def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))

def ta_kdj(data, fastk_period=10, slowk_period=3, slowd_period=3):
    indicators={}
    #计算kd指标
    high_prices = np.array(data['high'])
    low_prices = np.array(data['low'])
    close_prices = np.array(data['close'])
    indicators['k' + str(j)], indicators['d' + str(j)] = ta.STOCH(high_prices, low_prices, close_prices,fastk_period=fastk_period,\
                                                slowk_period=slowk_period, slowk_matype = 0,\
                                                slowd_period=slowd_period, slowd_matype = 0)
    # indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
    # #调整J的值不超过100，不低于-100
    # temp = []
    # for i in indicators['j']:
    #     if i > 100:
    #         temp.append(100)
    #     elif i < 0:
    #         temp.append(0)
    #     else:
    #         temp.append(i)
    # indicators['j'] = np.array(temp)
    kdj = pd.DataFrame(indicators)
    return kdj

atr_n = 20
s_time = '2015-01-01'
e_time = '2019-04-26'
total_return = []
return_m = []

# symbol_list = ['SZSE.002456']
# symbol_list = ['SZSE.002236','SZSE.002555','SZSE.002456','SZSE.002285','SZSE.002833','SZSE.002572','SZSE.000002','SHSE.603288','SZSE.002508','SHSE.600340','SHSE.603898','SHSE.600585','SZSE.002081','SHSE.600690','SZSE.000333','SHSE.600741','SZSE.002294','SHSE.600066','SHSE.600398','SZSE.002085','SZSE.000651','SZSE.000887','SHSE.600388','SZSE.002142','SHSE.600036','SHSE.600612','SZSE.000848','SHSE.601318','SHSE.600660','SHSE.600104','SHSE.600273','SHSE.600987','SZSE.000423','SHSE.601009','SZSE.002275']
# symbol_list = ['SHSE.510050','SHSE.510500','SHSE.510880','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.518880'\
#     ,'SHSE.600036','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
#     ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
#     ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
#     ,'SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
#     ,'SZSE.002508','SZSE.002555','SZSE.002572','SZSE.002833','SZSE.159901','SZSE.159915','SZSE.159919']
# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']
# symbol_list = ['SHSE.603799','SZSE.002460','SHSE.600588','SZSE.300136','SHSE.600760','SHSE.600438','SZSE.300122','SHSE.601012','SHSE.601108','SHSE.603993','SZSE.002236','SZSE.300433','SZSE.002466','SZSE.002555','SHSE.600809','SHSE.601155','SZSE.002714','SZSE.002624','SZSE.002230','SZSE.002153','SZSE.002027','SZSE.002456','SZSE.002475','SHSE.600516','SZSE.000839','SHSE.600703','SHSE.600570','SZSE.300296','SZSE.000792','SZSE.002797','SZSE.002271','SZSE.300142','SZSE.300017','SZSE.002044','SZSE.002008','SHSE.603833','SZSE.300059','SZSE.300003','SZSE.002050','SZSE.002773','SZSE.002558','SZSE.000568','SZSE.300033','SHSE.600498','SZSE.000661','SZSE.002202','SZSE.000063','SZSE.002032','SZSE.002572','SHSE.600196','SZSE.000671','SZSE.300251','SHSE.601111','SHSE.600867','SZSE.300408','SHSE.600038','SZSE.002304','SZSE.300072','SZSE.002146','SHSE.601888','SZSE.000963','SHSE.600176','SHSE.600549','SHSE.600487','SHSE.600048','SHSE.600566','SHSE.600816','SZSE.002241','SZSE.002065','SZSE.000961','SZSE.000938','SZSE.000002','SHSE.600372','SZSE.002415','SHSE.600271','SZSE.300124','SZSE.300070','SZSE.002311','SHSE.600297','SHSE.603288','SHSE.600029','SZSE.002179','SHSE.600346','SZSE.002001','SHSE.601992','SZSE.000725','SZSE.002508','SZSE.000983','SZSE.000768','SZSE.300015','SHSE.600909','SZSE.000858','SZSE.002422','SZSE.001979','SHSE.600340','SHSE.601336','SZSE.002310','SZSE.002493','SZSE.000728','SZSE.002673','SHSE.601225','SHSE.601877','SZSE.000627','SHSE.601933','SHSE.600436','SHSE.601601','SHSE.600585','SHSE.600276','SHSE.600111','SZSE.002081','SZSE.300144','SHSE.600690','SHSE.601360','SZSE.002007','SZSE.000333','SHSE.600031','SHSE.600383','SHSE.600522','SZSE.000069','SHSE.600741','SHSE.600009','SHSE.600115','SHSE.600887','SHSE.601688','SZSE.002594','SZSE.002601','SHSE.600068','SHSE.601919','SZSE.002294','SHSE.601021','SZSE.000898','SZSE.000413','SHSE.601117','SHSE.600893','SZSE.300024','SHSE.601198','SHSE.600482','SHSE.601611','SZSE.000895','SHSE.600332','SHSE.600066','SHSE.601800','SHSE.600019','SHSE.600208','SHSE.600398','SZSE.002085','SHSE.601901','SZSE.002602','SZSE.000651','SZSE.002024','SHSE.600109','SHSE.600362','SZSE.002352','SHSE.600352','SHSE.600977','SHSE.600518','SHSE.600011','SZSE.000826','SHSE.600061','SHSE.600958','SZSE.000538','SZSE.000338','SZSE.000709','SHSE.600535','SHSE.601555','SHSE.601607','SZSE.000402','SHSE.600583','SHSE.601628','SZSE.002142','SZSE.002736','SHSE.600999','SZSE.000425','SHSE.600118','SHSE.600010','SHSE.600369','SHSE.600036','SHSE.601186','SHSE.601899','SHSE.601333','SZSE.000783','SHSE.601377','SHSE.600998','SHSE.600153','SHSE.601318','SHSE.600018','SHSE.600606','SHSE.600660','SZSE.000001','SHSE.600519','SHSE.600547','SHSE.600030','SHSE.600050','SZSE.000100','SHSE.600104','SHSE.601238','SHSE.603858','SHSE.601788','SHSE.600027','SHSE.600705','SHSE.600085','SZSE.000776','SHSE.600739','SHSE.600489','SHSE.601211','SZSE.000423','SHSE.600406','SHSE.601088','SHSE.601668','SZSE.002450','SHSE.600837','SHSE.601669','SHSE.600089','SHSE.600637','SHSE.601018','SZSE.000630','SHSE.601766','SZSE.000625','SHSE.601939','SHSE.600926','SHSE.601618','SHSE.601997','SZSE.000876','SHSE.601009','SHSE.600415','SHSE.600028','SHSE.601998','SHSE.601989','SHSE.600886','SHSE.601006','SZSE.000166','SHSE.601398','SHSE.600688','SHSE.601727','SHSE.601229','SZSE.000157','SHSE.601390','SHSE.600170','SHSE.601818','SHSE.601288','SHSE.600000','SHSE.601857','SHSE.601985','SHSE.600023','SHSE.600919','SHSE.601166','SHSE.600674','SHSE.600015','SHSE.600177','SHSE.600900','SHSE.601988','SHSE.601169','SHSE.601328','SHSE.600795','SHSE.600016']
# symbol_list = ['SHSE.601360','SHSE.601108','SHSE.600816','SZSE.002797','SHSE.600588','SHSE.600516','SZSE.000839','SHSE.600760','SZSE.300033','SZSE.002558','SZSE.002460','SHSE.600438','SZSE.300017','SZSE.000792','SZSE.000063','SZSE.002153','SZSE.002714','SHSE.603799','SHSE.600346','SZSE.002450','SHSE.603993','SZSE.002466','SZSE.000671','SHSE.600909','SZSE.002230','SZSE.300072','SHSE.600867','SZSE.000938','SZSE.300142','SHSE.600271','SZSE.002673','SZSE.002602','SZSE.300122','SHSE.601012','SHSE.601155','SZSE.002146','SHSE.601992','SZSE.002044','SZSE.002493','SHSE.603833','SZSE.002310','SZSE.000661','SZSE.300059','SZSE.000961','SHSE.600570','SHSE.600518','SZSE.002202','SZSE.000627','SHSE.600061','SZSE.002050','SHSE.600369','SZSE.002555','SZSE.000413','SZSE.300433','SHSE.600111','SZSE.000728','SZSE.002236','SZSE.002085','SZSE.300136','SHSE.600340','SHSE.601198','SHSE.600372','SHSE.600703','SZSE.000100','SZSE.000725','SZSE.000876','SZSE.002007','SZSE.002773','SZSE.300296','SZSE.002624','SHSE.600050','SHSE.600809','SZSE.000709','SHSE.600549','SHSE.600208','SHSE.600498','SZSE.002065','SZSE.300251','SHSE.601888','SZSE.000002','SHSE.601555','SZSE.300003','SZSE.002736','SZSE.002001','SHSE.600332','SZSE.000783','SZSE.300070','SHSE.601727','SHSE.600958','SHSE.601901','SHSE.601919','SZSE.002572','SHSE.600482','SHSE.601377','SHSE.601111','SZSE.002027','SZSE.000768','SHSE.600048','SHSE.600109','SHSE.600297','SZSE.000963','SHSE.600398','SZSE.300024','SHSE.600010','SZSE.002456','SHSE.600406','SHSE.600487','SHSE.601611','SHSE.600038','SHSE.600029','SHSE.600436','SZSE.002352','SZSE.002601','SZSE.002032','SHSE.600176','SHSE.600566','SZSE.001979','SHSE.600115','SZSE.002008','SZSE.300015','SHSE.601788','SZSE.002422','SHSE.600276','SZSE.000983','SZSE.300144','SHSE.601933','SZSE.002594','SHSE.600739','SHSE.600118','SHSE.601800','SZSE.002475','SHSE.600196','SZSE.002304','SHSE.600705','SZSE.002179','SHSE.601877','SHSE.600383','SZSE.002271','SHSE.601688','SHSE.600606','SZSE.000898','SHSE.600999','SHSE.600547','SZSE.002311','SHSE.601989','SZSE.002241','SHSE.600522','SHSE.600535','SHSE.600893','SHSE.600018','SHSE.600583','SHSE.601336','SHSE.600837','SZSE.300408','SHSE.601021','SHSE.600009','SHSE.600030','SHSE.600068','SZSE.002081','SHSE.600011','SHSE.601088','SHSE.601186','SHSE.601238','SZSE.000069','SHSE.601618','SZSE.000001','SHSE.600019','SHSE.600352','SHSE.600066','SHSE.601899','SZSE.000826','SZSE.000402','SHSE.600362','SZSE.002415','SZSE.000776','SHSE.601018','SHSE.600489','SZSE.002024','SHSE.600027','SHSE.601669','SHSE.603288','SHSE.601117','SZSE.000425','SZSE.000568','SZSE.000625','SHSE.600637','SHSE.601225','SZSE.300124','SHSE.600977','SHSE.600741','SHSE.600585','SZSE.000166','SHSE.601601','SHSE.600690','SZSE.002294','SHSE.600031','SZSE.000895','SZSE.002508','SHSE.600887','SHSE.603858','SHSE.601390','SHSE.600926','SZSE.002142','SZSE.000630','SHSE.601766','SHSE.600085','SZSE.000338','SZSE.000858','SHSE.601998','SHSE.600415','SHSE.601211','SZSE.000538','SHSE.601628','SHSE.601997','SHSE.600089','SHSE.601333','SHSE.601607','SHSE.601668','SHSE.600998','SHSE.600153','SHSE.600036','SHSE.601318','SZSE.000651','SHSE.601009','SHSE.600519','SHSE.600795','SHSE.601939','SZSE.000333','SHSE.600170','SHSE.600028','SHSE.600919','SHSE.600660','SZSE.000423','SHSE.601985','SHSE.601398','SHSE.601229','SHSE.600104','SHSE.600023','SHSE.601288','SHSE.601818','SHSE.600688','SZSE.000157','SHSE.600000','SHSE.600177','SHSE.601857','SHSE.601166','SHSE.601006','SHSE.600015','SHSE.600016','SHSE.601988','SHSE.600886','SHSE.601169','SHSE.601328','SHSE.600674','SHSE.600900']
# symbol_list = ['SHSE.601012','SHSE.601108','SHSE.601155','SHSE.603993','SHSE.603799','SZSE.000792','SZSE.000839','SZSE.002044','SZSE.002153','SZSE.002230','SZSE.002460','SZSE.002466','SZSE.002558','SZSE.002714','SZSE.002797','SZSE.300017','SZSE.300122','SZSE.300142']
# symbol_list = ['SHSE.600271','SHSE.600346','SHSE.600438','SHS.600516','SHSE.600570','SHSE.600588','SHSE.600703','SHSE.600760','SHSE.600809','SHSE.600816','SHSE.600867','SHSE.600909','SHSE.601012','SHSE.601108','SHSE.601155','SHSE.601360','SHSE.601992','SHSE.603799','SHSE.603833','SHSE.603993','SZSE.000063','SZSE.000671','SZSE.000792','SZSE.000839','SZSE.000938','SZSE.002008','SZSE.002027','SZSE.002044','SZSE.002050','SZSE.002146','SZSE.002153','SZSE.002230','SZSE.002236','SZSE.002271','SZSE.002450','SZSE.002456','SZSE.002460','SZSE.002466','SZSE.002475','SZSE.002555','SZSE.002558','SZSE.002602','SZSE.002624','SZSE.002673','SZSE.002714','SZSE.002773','SZSE.002797','SZSE.300003','SZSE.300017','SZSE.300033','SZSE.300059','SZSE.300072','SZSE.300122','SZSE.300136','SZSE.300142','SZSE.300296','SZSE.300433']
# symbol_list = ['SHSE.600036','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456'\
#     ,'SZSE.002508','SZSE.002555','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585'\
#     ,'SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288'\
#     ,'SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081'\
#     ,'SZSE.002085','SZSE.002142','SZSE.002572','SZSE.002833']

symbol_list = ['SHSE.600271','SHSE.600346','SHSE.600438','SHSE.600516','SHSE.600570','SHSE.600588','SHSE.600703','SHSE.600760','SHSE.600809','SHSE.600816','SHSE.600867','SHSE.600909','SHSE.601012','SHSE.601108','SHSE.601155','SHSE.601360','SHSE.601992','SHSE.603799','SHSE.603833','SHSE.603993','SZSE.000063','SZSE.000671','SZSE.000792','SZSE.000839','SZSE.000938','SZSE.002008','SZSE.002027','SZSE.002044','SZSE.002050','SZSE.002146','SZSE.002153','SZSE.002230','SZSE.002236','SZSE.002271','SZSE.002450','SZSE.002456','SZSE.002460','SZSE.002466','SZSE.002475','SZSE.002555','SZSE.002558','SZSE.002602','SZSE.002624','SZSE.002673','SZSE.002714','SZSE.002773','SZSE.002797','SZSE.300003','SZSE.300017','SZSE.300033','SZSE.300059','SZSE.300072','SZSE.300122','SZSE.300136','SZSE.300142','SZSE.300296','SZSE.300433','SHSE.600036','SZSE.002146','SZSE.002236','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002456','SZSE.002508','SZSE.002555','SHSE.600066','SHSE.600104','SHSE.600273','SHSE.600340','SHSE.600388','SHSE.600398','SHSE.600585','SHSE.600612','SHSE.600660','SHSE.600690','SHSE.600741','SHSE.600987','SHSE.601009','SHSE.601318','SHSE.603288','SHSE.603898','SZSE.000002','SZSE.000333','SZSE.000423','SZSE.000651','SZSE.000848','SZSE.000887','SZSE.002081','SZSE.002085','SZSE.002142','SZSE.002572','SZSE.002833']

years = int(e_time[:4]) - int(s_time[:4]) + 1
start_year = s_time
end_year = e_time

for sym in symbol_list:
# 查询历史行情
#     df_k = history(symbol=sym, frequency='1h', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
#     df_data = get_stk(sym, start_year, end_year)
    df_data = get_stk_1h(sym,start_year, end_year)
    if len(df_data) == 0:
        continue
    df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
    df_data.loc[:, 'chg'] = (df_data['close'] - df_data['close'].shift(1)) / df_data['close'].shift(1)

    cci_n= [15,30,60]
    cci_m = pd.DataFrame()
    for n in cci_n:
        cci_m = pd.concat([cci_m, ta_cci(n, df_data)], axis=1)
    df_data = pd.concat([df_data, cci_m], axis=1)
    # for ma_n in [5,34]:#[3,5,20,34,60,120]:
    #     # df_data.loc[:, 'ace'] = df_data['close'] * 0.382 + 0.206 *(df_data['high'] + df_data['low'] + df_data['open'])
    #     df_data.loc[:,'ma'+str(ma_n)] = df_data.close.rolling(ma_n,min_periods=0).mean()

    # df_data.loc[:, 'ma_chg'] = df_data['ma5'] - df_data['ma34']
    # # df_data.loc[:, 'ma_avg5'] = df_data['ma_chg'].rolling(5,min_periods=0).mean()
    # df_data.loc[:, 'ma_avg20'] = df_data['ma_chg'].rolling(20,min_periods=0).mean()

    kdj_n = [10, 20, 40]
    for j in kdj_n:
        k = int(j / 3)
        df_data = pd.concat([df_data, ta_kdj(df_data, j, k, k)], axis=1)
    df_data = df_data.dropna()

    # re, mdd, df_r = Run(df_data)
    Run_aa(df_data)
    Run_ao(df_data)
    # total_return.append([sym,re,mdd])
    # print(total_return[-1])
# # #
# ret = pd.DataFrame(total_return, columns=['symbol', 'return', 'mdd'])
# print(ret)
#
# # filename = time.strftime('%Y%m%d_%H%M%S') + '.csv'
# # t_r=pd.DataFrame(list(total_return))
# # t_r.to_csv(filename)