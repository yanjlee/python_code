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
from STK.tsdata import get_k_stk as get_k, get_stk,get_stk_1h
import statsmodels.api as sm # 最小二乘
import copy
#from statsmodels.stats.outliers_influence import summary_table # 获得汇总信息
#from sklearn.preprocessing import MinMaxScaler, StandardScaler



# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

def Run_pro(dataset):
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

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        k = row[1].k
        d = row[1].d
        ma5 = row[1].ma5
        ma34 = row[1].ma34

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        ## KDJ策略
        if k > d and ma5 > ma34:# and pre_k < pre_d:
            signal = 1
        else:
            signal = 0

        # ##ATR 止损
        # if signal == 1:
        #     max_price = max(max_price, row[1].high)
        # else:
        #     max_price = 0
        #
        # if close < (max_price - 2.2 * atr) and signal == 1:
        #     signal = 0
        # # elif b_day != 0:
        #     signal = 0
        #
        # ##百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # if b_day != 0:
        #     signal = 0
        #
        # if pre_pos == 0 and signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_pos = signal

    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_p`os for rt in rt_list]
    df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['c_pro'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    # df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['c_pro'])
    # df_rt.to_csv('test.csv')
    return(df_rt['c_pro'].iloc[-1], max_draw_down,df_rt['c_pro'])


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

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        k = row[1].k
        d = row[1].d

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        ## KDJ策略
        if k > d:# and pre_k < pre_d:
            signal = 1
        elif k < d:# and pre_k > pre_d:
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
        #     signal = 0
        #
        # ##百分比止损
        # stop_loss = 0.05
        # if signal == 1 and close < buy_price * (1 - stop_loss):
        #     signal = 0
        # if b_day != 0:
        #     signal = 0
        #
        # if pre_pos == 0 and signal == 1:
        #     buy_price = pre_close
        # elif pre_pos == 1 and signal == 0:
        #     buy_price = 0
        #     b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_pos = signal
        pre_k = k
        pre_d = d


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
    # df_rt.to_csv('test.csv')
    return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt[['cum_rate', 'raw_cret']])


def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))

# def kdj_pro(kdata, fastk_period=9, slowk_period=3, slowd_period=3):
#     data = kdata
#     data.loc[:, 'rate'] = data.volume / data.volume.rolling(fastk_period,min_periods=1).sum()
#     data.loc[:, 'high_w'] = data.rate * data.high
#     data.loc[:, 'low_w'] = data.rate * data.low
#     data.loc[:, 'close_w'] = data.rate * data.close
#     data.loc[:, 'open_w'] = data.rate * data.open
#     data.loc[:, 'high_wc'] = data.high_w.rolling(fastk_period,min_periods=1).sum()
#     data.loc[:, 'low_wc'] = data.low_w.rolling(fastk_period,min_periods=1).sum()
#     data.loc[:, 'close_wc'] = data.close_w.rolling(fastk_period,min_periods=1).sum()
#     data.loc[:, 'open_wc'] = data.open_w.rolling(fastk_period,min_periods=1).sum()
#     data = data.drop(columns = ['open','high','low','close','open_w','high_w','low_w','close_w','volume','rate'])
#     indicators={}
#     #计算kd指标
#     high_prices = np.array(data['high_wc'])
#     low_prices = np.array(data['low_wc'])
#     close_prices = np.array(data['close_wc'])
#     indicators['k'], indicators['d'] = ta.STOCH(high_prices, low_prices, close_prices,fastk_period=fastk_period,\
#                                                 slowk_period=slowk_period, slowk_matype = 1,\
#                                                 slowd_period=slowd_period, slowd_matype = 1)
#     data.rename(columns={'open_wc': 'open', 'high_wc': 'high', 'low_wc': 'low', 'close_wc': 'close'}, inplace=True)
#     kdj = pd.DataFrame(indicators).round(2)
#     data = pd.concat([data, kdj], axis=1)
#     return data

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
    kdj = pd.DataFrame(indicators).round(3)
    return kdj

def ta_kd(data, fastk_period=9, slowk_period=3, slowd_period=3):
    indicators={}
    #计算kd指标
    high_prices = np.array(data['high'])
    low_prices = np.array(data['low'])
    close_prices = np.array(data['close'])
    indicators['k'], indicators['d'] = ta.STOCH(high_prices, low_prices, close_prices,fastk_period=fastk_period,\
                                                slowk_period=slowk_period, slowk_matype = 0,\
                                                slowd_period=slowd_period, slowd_matype = 0)
    # matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
    kdj = pd.DataFrame(indicators).round(3)
    return kdj

# atr_n = 20
s_time = '2018-12-01'
e_time = '2019-05-20'
total_return = []
return_m = []

# symbol_list = ['SZSE.002714','SZSE.300033','SZSE.000839','SHSE.600816','SZSE.000876','SHSE.601012','SHSE.600438','SHSE.600703','SHSE.600518','SZSE.002555','SHSE.600061','SZSE.300136','SHSE.600867','SZSE.002572','SHSE.601108','SZSE.002624','SHSE.600588','SHSE.601555','SHSE.600273','SZSE.002797','SZSE.000961','SZSE.300017','SHSE.603833','SZSE.300072','SZSE.002456']
symbol_list = ['SHSE.512880']
# symbol_list = ['SHSE.603799', 'SZSE.002460', 'SHSE.600588', 'SZSE.300136', 'SHSE.600760', 'SHSE.600438', 'SZSE.300122', 'SHSE.601012', 'SHSE.601108', 'SHSE.603993',\
#                'SZSE.002236', 'SZSE.300433', 'SZSE.002466', 'SZSE.002555', 'SHSE.600809', 'SHSE.601155', 'SZSE.002714', 'SZSE.002624', 'SZSE.002230', 'SZSE.002153', \
#                'SZSE.002027']#, 'SZSE.002456', 'SZSE.002475', 'SHSE.600516', 'SZSE.000839', 'SHSE.600703']#, 'SZSE.002285', 'SHSE.600570', 'SZSE.300296', 'SZSE.000792', 'SZSE.002797', 'SZSE.002271', 'SZSE.300142', 'SZSE.300017', 'SZSE.002044', 'SZSE.002008', 'SHSE.603833', 'SZSE.300059', 'SZSE.300003', 'SZSE.002833', 'SZSE.002050', 'SZSE.002773', 'SZSE.002558', 'SZSE.000568', 'SZSE.300033', 'SHSE.600498', 'SZSE.000661', 'SZSE.002202', 'SZSE.000063', 'SZSE.002032', 'SZSE.002572', 'SHSE.600196', 'SZSE.000671', 'SZSE.300251', 'SHSE.601111', 'SHSE.600867', 'SZSE.300408', 'SHSE.600038', 'SZSE.002304', 'SZSE.300072', 'SZSE.002146', 'SHSE.601888', 'SZSE.000963', 'SHSE.600176', 'SHSE.600549', 'SHSE.600487', 'SHSE.600048', 'SHSE.600566', 'SHSE.600816', 'SZSE.002241', 'SZSE.002065', 'SZSE.000961', 'SZSE.000938', 'SZSE.000002', 'SHSE.600372', 'SZSE.002415', 'SHSE.600271', 'SZSE.300124', 'SZSE.300070', 'SZSE.002311', 'SHSE.600297', 'SHSE.603288', 'SHSE.600029', 'SZSE.002179', 'SHSE.600346', 'SZSE.002001', 'SHSE.601992','SZSE.000725', 'SZSE.002508', 'SZSE.000983', 'SZSE.000768', 'SZSE.300015', 'SHSE.600909', 'SZSE.000858', 'SZSE.002422', 'SZSE.001979', 'SHSE.600340', 'SHSE.601336', 'SZSE.002493', 'SZSE.002310', 'SZSE.000728', 'SZSE.002673', 'SHSE.601225', 'SHSE.601877', 'SZSE.000627', 'SHSE.603898', 'SHSE.601933', 'SHSE.600436', 'SHSE.601601', 'SHSE.600585', 'SHSE.600276', 'SHSE.600111', 'SZSE.300144', 'SZSE.002081', 'SHSE.600690', 'SHSE.601360', 'SZSE.002007', 'SZSE.000333', 'SHSE.600031', 'SHSE.600383', 'SHSE.600522', 'SZSE.000069', 'SHSE.600741', 'SHSE.600009', 'SHSE.600115', 'SHSE.601688', 'SHSE.600887', 'SZSE.002594', 'SZSE.002601', 'SHSE.600068', 'SHSE.601919', 'SZSE.002294', 'SHSE.601021', 'SZSE.000898', 'SZSE.000413', 'SHSE.601117', 'SHSE.600893', 'SZSE.300024', 'SHSE.601198', 'SHSE.600482', 'SHSE.601611', 'SZSE.000895', 'SHSE.600332', 'SHSE.600066', 'SHSE.601800', 'SHSE.600208', 'SHSE.600019', 'SHSE.600398', 'SHSE.601901', 'SZSE.002085', 'SZSE.002602', 'SZSE.000651', 'SZSE.002024', 'SHSE.600362', 'SHSE.600109', 'SZSE.002352', 'SHSE.600352', 'SHSE.600977', 'SHSE.600518', 'SHSE.600011', 'SZSE.000826', 'SHSE.600061', 'SHSE.600958', 'SZSE.000538', 'SZSE.000338', 'SZSE.000709', 'SHSE.600535', 'SHSE.601555', 'SHSE.601607', 'SZSE.000887', 'SHSE.600388', 'SZSE.000402', 'SHSE.600583', 'SHSE.601628', 'SZSE.002142', 'SZSE.002736', 'SHSE.600999', 'SZSE.000425', 'SHSE.600118', 'SHSE.600010', 'SHSE.600369', 'SHSE.600036', 'SHSE.600612', 'SHSE.601186', 'SHSE.601899', 'SZSE.000848', 'SHSE.601333', 'SZSE.000783', 'SHSE.601377', 'SHSE.600998', 'SHSE.600153', 'SHSE.601318', 'SHSE.600018', 'SHSE.600660', 'SHSE.600606', 'SZSE.000001', 'SHSE.600519', 'SHSE.600547', 'SHSE.600030', 'SHSE.600050', 'SZSE.000100', 'SHSE.600104', 'SHSE.601238', 'SHSE.603858', 'SHSE.601788', 'SHSE.600027', 'SHSE.600705', 'SHSE.600085', 'SZSE.000776', 'SHSE.600739', 'SHSE.600489', 'SHSE.600273', 'SHSE.600987', 'SHSE.601211', 'SZSE.000423', 'SHSE.600406', 'SHSE.601088', 'SHSE.601668', 'SZSE.002450', 'SHSE.600837', 'SHSE.601669', 'SHSE.600089', 'SHSE.600637', 'SHSE.601018', 'SZSE.000630', 'SHSE.601766', 'SZSE.000625', 'SHSE.601939', 'SHSE.600926', 'SHSE.601618', 'SHSE.601997', 'SZSE.000876', 'SHSE.601009', 'SHSE.600415', 'SHSE.600028', 'SHSE.601998', 'SZSE.002275', 'SHSE.601989', 'SHSE.601006', 'SHSE.600886', 'SZSE.000166', 'SHSE.601398', 'SHSE.600688', 'SHSE.601727', 'SHSE.601229', 'SZSE.000157', 'SHSE.601390', 'SHSE.600170', 'SHSE.601818', 'SHSE.601288', 'SHSE.600000', 'SHSE.601857', 'SHSE.601985', 'SHSE.600919', 'SHSE.600023', 'SHSE.601166', 'SHSE.600674', 'SHSE.600015', 'SHSE.600177', 'SHSE.600900', 'SHSE.601988', 'SHSE.601169', 'SHSE.601328', 'SHSE.600795', 'SHSE.600016']

years = int(e_time[:4]) - int(s_time[:4]) + 1
start_year = s_time
end_year = e_time

# for sym in symbol_list:
# # 查询历史行情
#     df_data = history(symbol=sym, frequency='1h', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
# #     df_data = get_stk(sym, start_year, end_year)
#     df_data = df_data.rename(columns={'eob':'datetime'})
#     print(df_data.columns)
#     # df_data = get_stk_1h(sym, start_year, end_year)
#     if len(df_data) == 0:
#         continue
# #     # df_data.loc[:,'atr'] = ta.ATR(df_data.high, df_data.low, df_data.close, timeperiod=atr_n)
#     df_data.loc[:, 'chg'] = (df_data['close'] - df_data['close'].shift(1)) / df_data['close'].shift(1)
#     df = df_data[['datetime', 'close', 'high', 'low','chg']].copy()

    # df_data = pd.concat([df_data, ta_kdj(df_data)], axis=1)
    # df_data = df_data.dropna()
    # re, mdd, df_k = Run(df_data)
    # total_return.append([sym,re,mdd])
    # #
    # # df_data.loc[:, 'ma5'] = df_data.close.rolling(3,min_periods=0).mean()
    # # df_data.loc[:, 'ma34'] = df_data.close.rolling(13,min_periods=0).mean()
    #
    # df = pd.concat([df, ta_kd(df)], axis=1)
    # df = df.dropna()
    # re_2, mdd_2, df_r_2 = Run(df)
    # # df_r_2.rename(columns={'cum_rate': 'cum_wtd'}, inplace=True)
    # total_return.append([sym,re_2,mdd_2])
    # df_k = pd.concat([df_k,df_r_2],axis = 1)
    # print(total_return[-2])
    #
    # ax = df_k.plot(title=sym)
    # fig = ax.get_figure()
    # fig.savefig(sym + '_kdj' + '.png')
    # plt.close(fig)



# # #
# ret = pd.DataFrame(total_return, columns=['symbol', 'return', 'mdd'])
# print(ret)
#
# # filename = time.strftime('%Y%m%d_%H%M%S') + '.csv'
# # t_r=pd.DataFrame(list(total_return))
# # t_r.to_csv(filename)