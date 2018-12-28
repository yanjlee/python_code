# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from ConnectDB import get_all_data, fill_data
from string import digits
from datetime import datetime, timedelta

set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')
# data = history(symbol='SHSE.600000', frequency='1d', start_time='2015-01-01', end_time='2015-12-31', fields='open,high,low,close')
# symbol_list = ['SHFE.rb1901']


def UpdateFutureData(symbol_m, symbol, stime, etime):
    fur_data = history(symbol=symbol_m, frequency='60s', start_time = stime, end_time = etime, fields='open,high,low,close,volume,position,bob', df = 'True')
    if len(fur_data) > 0:
        for i in range(0, len(fur_data)):
            data_string = str(list(fur_data.iloc[i])).replace('[Timestamp(','(\'' + symbol + '\',' ).replace(')','').replace(']',');')
            insert_sql =  'insert into data.fur_price_1m (symbol, datetime, close, high, low, open, position, volume) values' + data_string
            try:
                fill_data(insert_sql)
            except Exception as e:
                print(e)
                print(insert_sql)
        # print(symbol_m + ' is updated.')


def UpdateList(start_time, end_time):
    n_days = int((datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')).days/15 + 1)

    items = 'symbol'
    table = 'fur_info'
    condition = ' where symbol not like \'SP%\'  having length(symbol) > 3 order by symbol'
    symbol_info = get_all_data(items, table, condition)
    symbol_list = str(symbol_info).replace('(','').replace('),','').replace(',))','').replace('\'','').split(', ')

    items = 'code, market'
    table = 'fur_td_info'
    condition = '  order by code'
    code_info = get_all_data(items, table, condition)
    code_list = dict(code_info)

    for symbol in symbol_list:
        remove_digits = str.maketrans('', '', digits)
        symbol_type = symbol.translate(remove_digits)
        symbol_mkt = code_list[symbol_type]
        if symbol_mkt == 'CFE':
            symbol_m = 'CFFEX.' + symbol.lower()
        elif symbol_mkt == 'SHF':
            symbol_m = 'SHFE.' + symbol.lower()
        elif symbol_mkt == 'CZC':
            symbol_m = 'CZCE.' + symbol.lower()
        else:
            symbol_m = symbol_mkt + '.' + symbol.lower()

        stime = start_time
        for n in range(1, n_days+1):
            etime = (datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=15*n)).strftime('%Y-%m-%d %H:%M:%S')
            if etime > end_time:
                etime = end_time

            print(symbol + ': ' + stime + ' ~ ' + etime)
            UpdateFutureData(symbol_m,symbol,stime,etime)
            stime = etime

    symbols_cm = ['CFFEX.IC','CFFEX.IF','CFFEX.IH','CFFEX.T','CFFEX.TF','CZCE.CF','CZCE.FG','CZCE.JR','CZCE.LR','CZCE.MA','CZCE.OI','CZCE.PM','CZCE.RI','CZCE.RM','CZCE.RS','CZCE.SF','CZCE.SM','CZCE.SR','CZCE.TA','CZCE.WH','CZCE.ZC','DCE.A','DCE.B','DCE.BB','DCE.C','DCE.CS','DCE.FB','DCE.I','DCE.J','DCE.JD','DCE.JM','DCE.L','DCE.M','DCE.P','DCE.PP','DCE.V','DCE.Y','SHFE.AG','SHFE.AL','SHFE.AU','SHFE.BU','SHFE.CU','SHFE.FU','SHFE.HC','SHFE.NI','SHFE.PB','SHFE.RB','SHFE.RU','SHFE.SN','SHFE.WR','SHFE.ZN']
    symbols_c = ['IC','IF','IH','T','TF','CF','FG','JR','LR','MA','OI','PM','RI','RM','RS','SF','SM','SR','TA','WH','ZC','A','B','BB','C','CS','FB','I','J','JD','JM','L','M','P','PP','V','Y','AG','AL','AU','BU','CU','FU','HC','NI','PB','RB','RU','SN','WR','ZN']
    for i in range(0,len(symbols_cm)):
        stime = start_time
        for n in range(1, n_days+1):
            etime = (datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=15*n)).strftime('%Y-%m-%d %H:%M:%S')
            if etime > end_time:
                etime = end_time

            print(symbols_cm[i] + ': ' + stime + ' ~ ' + etime)
            UpdateFutureData(symbols_cm[i],symbols_c[i],stime,etime)
            stime = etime


def get_time():
    items = 'max(datetime)'
    tables = 'data.fur_price_1m'
    condition = ' '
    date_info = get_all_data(items, tables, condition)
    start_time = date_info[0][0].strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return(start_time,end_time)



start, end = get_time()
UpdateList(start, end)