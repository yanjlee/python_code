from datetime import datetime, timedelta
import pandas as pd
from ConnectDB import get_all_data


# 生成K线时间轴(Stock)
def time_list_stk(n):
    if n <2:
        print('n should be larger than 1, or you can use 1 minute data directly.')

    day_list = []
    for i in range(0, 330):
        times = (datetime.strptime('09:30', '%H:%M') + timedelta(minutes=i)).strftime('%H:%M')
        if times >= '11:30' and times < '13:00':
            continue
        day_list.append(times)

    def k_time(n, time_list):
        k_list = []
        for s in range(0, n):
            temp_list = []
            for t in range(s, len(time_list), n):
                if time_list[t] < '14:57':
                    temp_list.append(time_list[t])
            temp_list.append('14:57')
            k_list.append(temp_list)
        return (k_list)

    day_time = k_time(n, day_list)
    return (day_time)


# 获取stk数据
def get_stk_data(symbol, start_time, end_time):
    items = 'dtime, open, high, low, close'#, volume'
    table = ' td_price_1m'
    condition = 'where symbol = \'' + symbol + '\' and dtime >= \'' + start_time + '\' and dtime <= \'' + end_time + '\'  order by dtime asc'
    symbol_data = get_all_data(items, table, condition)
    k_data = pd.DataFrame(list(symbol_data), columns=['dtime', 'open', 'high', 'low', 'close'])#, 'volume'])
    k_data.rename(columns={'dtime': 'datetime'}, inplace=True)
    k_data.set_index(["datetime"], inplace=True)
    k_days = []
    if len(k_data) != 0:
        k_days = list(k_data.index.strftime('%Y-%m-%d'))
        k_days = sorted(set(k_days), key=k_days.index)
    return (k_data.astype('float64'), k_days)

def PreMin(times):
    pre_time = (datetime.strptime(times, '%Y-%m-%d %H:%M') + timedelta(minutes=-1)).strftime('%Y-%m-%d %H:%M')
    return (pre_time)

# stock k线价格聚合
def k_line_stk(k_data, k_days, day_list):
    df_k = pd.DataFrame()
    for dates in k_days:
        # 生成日盘时间列表
        day_time_list = []
        for dt in day_list:
            day_time_list.append(dates + ' ' + dt)

        # 数据处理，生成日盘K线数据
        day_data = []
        for i in range(0, len(day_time_list)-1):
            df_day = k_data.loc[day_time_list[i]:PreMin(day_time_list[i + 1])]
            if len(df_day) == 0:
                continue
            day_data.append([df_day.index[0].strftime('%Y-%m-%d %H:%M:%S'), df_day.open[0], max(df_day.high),
                             min(df_day.low),df_day.close[-1]])#,df_day.volume.sum()])

        day_data = pd.DataFrame(day_data, columns=['datetime', 'open', 'high', 'low', 'close'])#, 'volume'])
        # day_data.set_index(["datetime"], inplace=True)
        df_k = pd.concat([df_k, day_data])
    return (df_k)


def get_k_stk(symbol, n, k, start_time, end_time):
    day_list = time_list_stk(n)
    k_data, k_days = get_stk_data(symbol, start_time, end_time)
    df_k = k_line_stk(k_data, k_days, day_list[k])
    df_k = df_k.reset_index()
    df_k = df_k.drop(columns = ['index'])
    return(df_k)

def get_stk(symbol, start_time, end_time):
    if symbol.startswith('SHSE'):
        sym = symbol.replace('SHSE.', '') + '.SH'
    else:
        sym = symbol.replace('SZSE.', '') + '.SZ'
    items = 'date, open, high, low, close'#, volume'
    table = ' stk_price_forward'
    condition = 'where symbol = \'' + sym + '\' and date >= \'' + start_time + '\' and date <= \'' + end_time + '\'  order by date asc'
    symbol_data = get_all_data(items, table, condition)
    k_data = pd.DataFrame(list(symbol_data), columns=['datetime', 'open', 'high', 'low', 'close'])#, 'volume'])
    k_data.set_index(["datetime"], inplace=True)
    k_data = k_data.astype('float64')
    k_data = k_data.reset_index(["datetime"])
    return (k_data)

def get_cb(symbol,types = '5'):
    items = 'datetime, open, high, low, close'#, volume'
    table = ' cb_price'
    condition = 'where symbol = \'' + symbol + '\' and type = \'' + types +  '\' order by datetime asc'
    symbol_data = get_all_data(items, table, condition)
    k_data = pd.DataFrame(list(symbol_data), columns=['datetime', 'open', 'high', 'low', 'close'])#, 'volume'])
    k_data.set_index(["datetime"], inplace=True)
    k_data = k_data.astype('float64')
    k_data = k_data.reset_index(["datetime"])
    return (k_data)

def get_stk_1h(symbol, start_time, end_time):
    items = 'dtime as date, open, high, low, close, volume'
    table = ' td_price_1h'
    condition = 'where symbol = \'' + symbol + '\' and dtime >= \'' + start_time + '\' and dtime <= \'' + end_time + '\'  order by dtime asc'
    symbol_data = get_all_data(items, table, condition)
    k_data = pd.DataFrame(list(symbol_data), columns=['datetime', 'open', 'high', 'low', 'close','volume'])
    k_data.set_index(["datetime"], inplace=True)
    k_data = k_data.astype('float64')
    k_data = k_data.reset_index(["datetime"])
    return (k_data)

# n = 60
# k = 0
# symbol = 'J0'
# start_time = '2018-01-01'
# end_time = '2018-12-31'


# df_k = get_stk(symbol, start_time, end_time)
# print(df_k)
#
# df =  get_k_stk(symbol, 60,0 , start_time, end_time)
# print(df)

# symbol = '127008'
# type = '5'
# df = get_cb(symbol,type)
# print(df)