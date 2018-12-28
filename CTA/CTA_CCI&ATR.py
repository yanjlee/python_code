# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

#
#

from datetime import timedelta, datetime as dt
import pandas as pd
from ConnectDB import get_all_data
import os
# import matplotlib.pyplot as plot
from decimal import Decimal
# import numpy as np
# import scipy as sp
import numpy as np
import talib as ta
import CTAMod.tsdata as ts

def get_units(future_list):
    items_unit = 'code, unit * min_chg as units'
    items_deposit = 'code, unit * deposit as deposit'
    items_endtime = 'code, td_time'
    table = 'fur_td_info'
    condition = 'order by code asc'
    code_unit = dict(get_all_data(items_unit, table, condition))
    code_deposit = dict(get_all_data(items_deposit, table, condition))
    code_endtime = dict(get_all_data(items_endtime, table, condition))

    future_units = {}
    future_deposit = {}
    future_endtime = {}
    for symbol in future_list:
        if len(symbol) == 6:
            future_units[symbol] = float(code_unit[symbol[0:2].upper()])
            future_deposit[symbol] = float(code_deposit[symbol[0:2].upper()])
            future_endtime[symbol] = code_endtime[symbol[0:2].upper()]
        else:
            future_units[symbol] = float(code_unit[symbol.upper()])
            future_deposit[symbol] = float(code_deposit[symbol.upper()])
            future_endtime[symbol] = code_endtime[symbol.upper()]
    return(future_units, future_deposit, future_endtime)

def Run(cn, k_data,units,deposit,endtime):
    #实参数据定义##########################
    FEE = 3.5
    units = units
    deposit = deposit
    stop_time = endtime


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

    if stop_time == '15:00':
        EndTime_1 = '14:55'
        EndTime_2 = '14:55'
    else:
        EndTime_1 = '14:55'
        EndTime_2 = (dt.strptime(stop_time, '%H:%M') + timedelta(minutes=-5)).strftime('%H:%M')


    # 获取数据, 创建DataFrame
    # future_type = symbol
    k_data['chg'] = k_data['close'] - k_data['close'].shift(1)
    df = k_data.dropna()
    df.astype('float64')
    df = df.reset_index('datetime')

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

            self.pnl = self.chg * self.pos * units
            self.fee = abs(self.pos - self.pre_pos) * FEE
            self.net_pnl = self.pnl - self.fee
            self.pnl_rate = self.net_pnl / (self.close - self.chg) / deposit


    # 策略和类初始化数据
    signal = 0
    pre_pos = 0
    rt_list = []
    atr = df.atr[0]

    max_price = 0
    min_price = df.close[0]

    pre_close = df.close[0]
    pre_cci_list = df[list(df.columns[-cn-2:-2])].iloc[1]

    for i, row in enumerate(df.iterrows()):
        datetime = row[1].datetime
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos

    ## 策略信号
        # CCI
        ci = 400
        range_value = 50

        signal_temp = [0]
        cci_list = row[1][-cn-2:-2]
        # print(cci_list)

        for j in range(0, cn):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            for i in range(-ci, ci + 1, range_value):
                if pre_cci < i and cci > i:
                    signal_temp.append(1)
                    break
                elif pre_cci > i and cci < i:
                    signal_temp.append(-1)
                    break

        if sum(signal_temp) >= 2:
            signal_cci = 1
        elif sum(signal_temp) < 0:
            signal_cci = 0
        else:
            signal_cci = pre_pos

        ## 保留前一天close数据
        pre_close = close
        pre_cci_list = cci_list


        if signal_cci == 1:# and signal_bolling == 1:
            signal = 1
        elif signal_cci == -1:# and signal_bolling == -1:
            signal = -1
        else:
            signal = 0


    ## ATR 止损
        if signal == 1:
            max_price = max(max_price, row[1].high)
            min_price = close
        elif signal == -1:
            max_price = 0
            min_price = min(min_price, row[1].low)
        else:
            max_price = 0
            min_price = close

        if close < (max_price - 2 * atr) and signal == 1:
            signal = 0
        elif close > (min_price + 2 * atr) and signal == -1:
            signal = 0

    ## 收市前清盘
        if (row[1][0][11:] >= EndTime_1 and row[1][0][11:] <= '15:00') or (row[1][0][11:] >= EndTime_2 and row[1][0][11:] <= stop_time):
            signal = 0


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
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    df_rt['cum_rate'].plot()
    df_rt = df_rt.set_index('datetime')
    df = df.set_index('datetime')
    df_rt = pd.concat([df_rt, df], axis=1)
    filename = dt.now().strftime('%Y%m%d_%H%M%S') + '.csv'
    df_rt.to_csv(filename)
    # print(df_rt)
    return(df_rt['cum_rate'].iloc[-1], max_draw_down)


def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))

total_return = []
# future_list = ['TA','RU1901','M1901','J1901','J1905','RB1901','RB1905','RB1810','ZN1811','ZN1810','CU1811']
# future_list = ['J1901','RB1901']
# future_list  = ['CU','J','M','RB','RU','ZN']

future_list = ['ZN1901']
future_units, future_deposit, futur_endtime = get_units(future_list)
start = '2018-08-04 09:00:00'
end = '2018-11-27 15:01:00'


for i in future_list:
    symbol = i
    units = future_units[i]
    deposit = future_deposit[i]
    endtime = futur_endtime[i]
    df_k = ts.Get_k(start, end, symbol)

    cci_n = [10,20,30]
    cci_len = len(cci_n)
    cci_m = pd.DataFrame()
    for n in cci_n:
        cci_m = pd.concat([cci_m, ta_cci(n, df_k)], axis=1)

    k_data = pd.concat([df_k, cci_m, ta_atr(21, df_k)], axis=1)
    k_data.rename(columns={'eob': 'datetime'}, inplace=True)
    k_data = k_data.dropna()

    re, mdd = Run(cci_len, k_data, units, deposit, endtime)
    total_return.append([symbol,re, mdd])
for item in total_return:
    print(item)

# filename = dt.now().strftime('%Y%m%d_%H%M%S') + '.csv'
# t_r=pd.DataFrame(list(total_return))
# t_r.to_csv(filename)
# os.system('C:/codes/Blackberry.m4a')