# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import datetime as dt, timedelta
import pandas as pd
from connect_db import get_all_data, fill_data_no_err
import talib as ta
import ht_trade as ht
import numpy as np


set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

# 指定表插入数据, 输入:表名/df数据, 无输出(仅适用于ts_price_1m/ts_price_1h)
def insert_td_data(table,ts_data):
    if len(ts_data) > 0:
        for i in range(0, len(ts_data)):
            insert_sql =  'insert into '+ table +' values(\'' + ts_data.symbol[i] + '\',\'' + dt.strftime(ts_data.bob[i],'%Y-%m-%d %H:%M:%S') + '\',' + str(round(ts_data.open[i],3)) + ',' + str(round(ts_data.high[i],3))+ ',' + str(round(ts_data.low[i],3)) + ',' + str(round(ts_data.close[i],3)) + ',' + str(round(ts_data.volume[i],0)) + ',' + str(round(ts_data.amount[i],0)) + ');'
            try:
                fill_data_no_err(insert_sql)
            except:
                pass

# 获取gm最后n条数据并写入本地表,可自定义: 频率/本地表名/symbol/最后n条数, 无输出
def get_gm_data(symbol_list,table, frequency, window=4):
    h_data = pd.DataFrame()
    for symbol in symbol_list:
        history_data = history_n(symbol, frequency, window, end_time=None, fields='symbol,bob,open,high,low,close,volume,amount', skip_suspended=True, fill_missing='Last',
                                 adjust=1, adjust_end_time='', df=True)
        # print(history_data)
        h_data = pd.concat([h_data, history_data],ignore_index=True)
    insert_td_data(table, h_data)


# 获取gm历史数据并写入本地表,可自定义: 频率/本地表名/symbol/开始&结束时间, 无输出
def update_gm_history(frequency,table,symbol_list, start, end):
    n_days = int((dt.strptime(end, '%Y-%m-%d %H:%M:%S') - dt.strptime(start,'%Y-%m-%d %H:%M:%S')).days / 15 + 1)
    for i in range(0,len(symbol_list)):
        stime = start
        for n in range(1, n_days+1):
            etime = (dt.strptime(start,'%Y-%m-%d %H:%M:%S') + timedelta(days=15*n)).strftime('%Y-%m-%d %H:%M:%S')
            if etime > end:
                etime = end
            print(symbol_list[i] + ': ' + stime + ' ~ ' + etime)
            history_data = history(symbol_list[i], frequency, start_time=stime, end_time=etime,
                                   fields='symbol,bob,open,high,low,close,volume,amount', skip_suspended=True,
                                   fill_missing='Last',
                                   adjust=1, adjust_end_time='', df=True)
            insert_td_data(table,history_data)
            stime = etime
        print(symbol_list[i] + ' is updated into ' + table)

def ta_kd(data, fastk_period=9, slowk_period=3, slowd_period=3):
    indicators={}
    #计算kd指标
    high_prices = np.array(data['high'])
    low_prices = np.array(data['low'])
    close_prices = np.array(data['close'])
    indicators['k'], indicators['d'] = ta.STOCH(high_prices, low_prices, close_prices,fastk_period=fastk_period,\
                                                slowk_period=slowk_period, slowk_matype = 1,\
                                                slowd_period=slowd_period, slowd_matype = 1)
    kd = pd.DataFrame(indicators).round(3)
    return kd


# 获取指定symbol的最后120条1小时K线时间序列数据,返回df矩阵
def get_1h_data(symbol):
    items = ' * from (SELECT symbol, datetime, open, high, low, close'
    table = 'ts_price_1h'
    condition = 'where symbol = \'' + symbol + '\' order by datetime desc limit 120) order by datetime asc'
    df_1h = pd.DataFrame(get_all_data(items,table,condition), columns=['symbol','datetime','open', 'high', 'low', 'close'])
    df_1h.sort_values('datetime', inplace=True)
    return(df_1h)


# 获取指定symbol,并晚于time参数的1分钟K线时间序列数据,返回df矩阵
def get_1m_data(symbol,time):
    items = 'symbol, datetime, open, high, low, close'
    table = 'ts_price_1m'
    condition = 'where symbol = \'' + symbol + '\' and datetime >= \'' + time + '\' order by datetime asc'
    df_1m = pd.DataFrame(get_all_data(items,table,condition), columns=['symbol','datetime','open', 'high', 'low', 'close'])
    df_1m.sort_values('datetime', inplace=True)
    return(df_1m)


def calc_kd(df_1h):
    k_data = pd.concat([df_1h, ta_kd(df_1h)], axis=1)
    k_data['chg'] = (k_data['close'] - k_data['close'].shift(1)) / k_data['close'].shift(1)
    # k_data.loc[:, 'ma3'] = k_data.close.rolling(3, min_periods=0).mean()
    # k_data.loc[:, 'ma13'] = k_data.close.rolling(13, min_periods=0).mean()
    df = k_data.dropna()

    # 计算signal、buy_price
    signals = [0]
    pre_pos = 0
    buy_price_list = [0]
    buy_price = 0
    pre_close = 0

    for i, row in enumerate(df.iterrows()):
        close = row[1].close
        open = row[1].open
        k = row[1].k
        d = row[1].d
        # ma3 = row[1].ma3
        # ma13 = row[1].ma13

        if i < 1:  # 从第二条开始
            continue

        ## 策略信号 风险较高加MA，风险较低去MA单用KD
        if k > d:# and ma3 > ma13
            signal = 1
        # elif k < d:
        #     signal = 0
        else:
            signal = 0

        signals.append(signal)
        ## 保留前一天close数据
        if pre_pos == 0 and signal == 1:
            buy_price = pre_close
        elif pre_pos == 1 and signal == 0:
            buy_price = 0
        elif pre_pos == 0 and signal == 0:
            buy_price = 0
        buy_price_list.append(buy_price)

        pre_pos = signal
        pre_close = close

    df_signal = pd.DataFrame({'signal': signals, 'buy_price': buy_price_list},
                             index=df.index)
    df = df.drop(['open', 'high', 'low', 'close', 'chg'], axis=1, inplace=False)  # 删除列
    df = pd.concat([df, df_signal], axis=1)
    df = df.round(3)
    return(df)


# 指定表插入计算信号数据, 输入:表名/df数据, 无输出(仅适用于td_cci)
def update_calc_data(symbol_list):
    for symbol in symbol_list:
        df_1h = get_1h_data(symbol) # 获取1h数据
        if len(df_1h) == 0:
            continue
        ts_data = calc_kd(df_1h)  # 计算指标
        if len(ts_data) > 0:
            # last_dict = get_last('td_cci', ts_data)
            for i in range(0, len(ts_data)):
                # if ts_data['datetime'].iloc[i] <= last_dict[ts_data.symbol.iloc[i]] or ts_data.symbol.iloc[i] not in last_dict.keys() or ts_data['datetime'].iloc[i][11:16] not in ['09:30','10:30','13:00','14:00']:
                #     continue
                insert_sql = 'insert into td_kd (\'symbol\',\'datetime\',\'k\',\'d\',\'signal\',\'buy_price\') values('+ str(list(ts_data.iloc[i])).replace('[','').replace(']','') + ');'
                try:
                    fill_data_no_err(insert_sql)
                except:
                    pass


# 计算最后1条小时K线之后, 1分钟多k线矩阵的聚合数据联合小时K线的信号指标, 标识最新买卖变动
# 输入: 各symbol的最后一条1小时k线的交易信号矩阵
# 输出: 各symbol的最后一条1小时k线 + 最后数分钟K线聚合数据的信号矩阵,每symbol各两条
def calc_current_td_signal(signal_data):
    for i in range(0, len(signal_data)): # 由当前最后一条小时k线时间判断开始时间点
        # if signal_data['datetime'][i][11:] == '09:30:00':
        #     final_time = signal_data['datetime'][0][:11] + '10:29:00'
        # elif signal_data['datetime'][i][11:] == '10:30:00':
        #     final_time = signal_data['datetime'][0][:11] + '11:29:00'
        # elif signal_data['datetime'][i][11:] == '13:00:00':
        #     final_time = signal_data['datetime'][0][:11] + '13:59:00'
        # elif signal_data['datetime'][i][11:] == '14:00:00':
        #     final_time = signal_data['datetime'][0][:11] + '09:29:00'
        final_time = signal_data['datetime'][0]
        # 获取最新多条1分钟数据, 聚合成1条K线拼接到1小时数据k线后, 重新计算CCI, 并将新纪录的信号数据插入到信号矩阵最后
        df_1h = get_1h_data(signal_data.symbol[i])
        df_1m = get_1m_data(signal_data.symbol[i], final_time)
        if len(df_1h) == 0 or len(df_1m) == 0:
            continue
        df_m2h = [df_1m.symbol[0],df_1m['datetime'].iloc[-1],df_1m.open[0],max(df_1m.high),min(df_1m.low),df_1m.close.iloc[-1]]
        df_1h.loc[-1] = df_m2h
        df_1h = df_1h.reset_index()
        df_data = calc_kd(df_1h)
        signal_data = signal_data.append(df_data[['symbol','datetime','signal','buy_price']].iloc[-1])

    signal_data = signal_data.reset_index()
    signal_data = signal_data.drop(['index'], axis=1, inplace=False)
    signal_data = signal_data.sort_values(by=['symbol', 'datetime'])
    return(signal_data)


# 获取最新(最后一条)交易信号数据, 输入: symbol_list, 输出: df交易信号矩阵
def get_td_signal(symbol_list):
    symbol_list = symbol_list
    items = 'a.symbol, a.datetime, a.signal, a.buy_price'
    table = 'td_kd a inner join (SELECT symbol, max(datetime) as dtime FROM td_kd group by symbol) b on a.symbol =b.symbol and a.datetime =b.dtime'
    condition = 'where a.symbol in (' + str(symbol_list).replace('[', '').replace(']','') + ') order by a.symbol asc'
    signal_data = get_all_data(items, table, condition)
    signal_data = pd.DataFrame(signal_data,columns=['symbol','datetime','signal','buy_price'])
    signal_data = calc_current_td_signal(signal_data)
    return(signal_data)

def get_td_signal_h(symbol_list):
    signal_data = pd.DataFrame()
    for symbol in symbol_list:
        items = 'symbol, datetime, signal, buy_price'
        table = 'td_kd'
        condition = 'where symbol = \'' + symbol + '\' order by datetime desc limit 2'
        kd_data = get_all_data(items, table, condition)
        if len(kd_data) == 0:
            continue
        kd_data = pd.DataFrame(kd_data,columns=['symbol','datetime','signal','buy_price'])
        signal_data = signal_data.append(kd_data)
    signal_data = signal_data.sort_values(by=['symbol', 'datetime'])
    return(signal_data)


def trade(symbol_list):
    signal_list = get_td_signal(symbol_list)
    s_list = []
    b_list = []
    signal_list = signal_list.reset_index(drop = True)
    for i in range(0, len(signal_list),2):
        if signal_list.signal[i+1] == 1:
            b_list.append(signal_list.symbol[i])
        else:
            s_list.append(signal_list.symbol[i])
    ht.trade_exe(s_list, b_list)


symbol_list = ['SHSE.000300','SZSE.000002','SZSE.000333','SHSE.512880','SHSE.601318','SHSE.600585','SHSE.600508','SHSE.600660','SHSE.603288','SHSE.603288']
# symbol_list = ['SHSE.512880']
start = '2019-05-18 08:54:00'
end = '2019-05-21 15:04:01'
# # # frequency = '60s'
# # # table = 'ts_price_1m'
frequency = '3600s'
table = 'ts_price_1h'
update_gm_history(frequency,table,symbol_list,start,end)
update_calc_data(symbol_list)

# print(df_t)
# df = calc_kd(get_1h_data(symbol_list[0]))
# df = ta_kd(get_1h_data(symbol_list[0]))

# df = get_td_signal(symbol_list)
# print(df)

# info = get_cci_signal(symbol_list)
# print(info)
# signal_list = get_td_signal(symbol_list)
# print(signal_list)