# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from ConnectDB import get_all_data, fill_data
# from string import digits
from datetime import datetime, timedelta

set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')


def InsertTdData(symbol, stime, etime):
    fur_data = history(symbol=symbol, frequency='60s', start_time = stime, end_time = etime, fields='open,high,low,close,volume,bob',fill_missing='Last',adjust=1, df = 'True')
    if len(fur_data) > 0:
        for i in range(0, len(fur_data)):
            data_string = str(list(fur_data.iloc[i])).replace('[Timestamp(','(\'' + symbol + '\',' ).replace(')','').replace(']',');')
            insert_sql =  'insert into data.td_price_1m (symbol, dtime, close, high, low, open, volume) values' + data_string
            try:
                fill_data(insert_sql)
            except Exception as e:
                print(e)
                print(insert_sql)



def UpdateInfo(start_time, end_time, symbol_list):
    n_days = int((datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')).days/15 + 1)
    for i in range(0,len(symbol_list)):
        stime = start_time
        for n in range(1, n_days+1):
            etime = (datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=15*n)).strftime('%Y-%m-%d %H:%M:%S')
            if etime > end_time:
                etime = end_time

            print(symbol_list[i] + ': ' + stime + ' ~ ' + etime)
            InsertTdData(symbol_list[i],stime,etime)
            stime = etime
        print(symbol_list[i] + ' is updated.')


def get_time():
    items = 'max(datetime)'
    tables = 'data.td_price_1m'
    condition = ' '
    date_info = get_all_data(items, tables, condition)
    start_time = date_info[0][0].strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return(start_time,end_time)


start, end = get_time()
# symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600508','SHSE.600660','SHSE.603288']
symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600508','SHSE.600660','SHSE.603288','SHSE.510880','SZSE.159901','SZSE.159915','SHSE.510500','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050']

UpdateInfo(start, end,symbol_list)