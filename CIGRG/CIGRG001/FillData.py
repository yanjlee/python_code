# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import logging as log
from pandas import DataFrame, Series
import datetime, time
from datetime import timedelta, datetime
import os
import tushare as ts
from ConnectDB import connDB, connClose, get_data, get_all_data

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level = log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format = "%(levelname)s: %(message)s")

items = 'symbol, date'
startDate = '2010-01-04'
endDate = '2018-03-16'
table = 'idx_price'
symbol_list = ['000001.SH']
db_data = get_data(items, table, symbol_list, startDate, endDate)

date_list = []
for i in range(0, len(db_data)):
    date_list.append(db_data[i][1])

conn, cur = connDB()

def fill_adj_stk(table):
    items2 = 'symbol, min(date), max(date)'
    table2 = table
    condition = ' group by symbol order by symbol'
    db_data2 = get_all_data(items2, table2, condition)


    for a in range(0, len(db_data2)):
        index_start = date_list.index(db_data2[a][1])
        index_end = date_list.index(db_data2[a][2]) + 1
        date_list_idx = date_list[index_start:index_end]

        item3 = 'date, close'
        table3 = table2
        symbol_list3 = '\'' + db_data2[a][0] + '\''
        startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
        endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
        stk_data = get_data(item3, table3, symbol_list3, startDate3, endDate3)
        date_stk = []
        close_stk = {}
        for b in range(0, len(stk_data)):
            date_stk.append(stk_data[b][0])
            close_stk[stk_data[b][0]] = stk_data[b][1]

        fill_stk = {}
        fill_stk[date_list_idx[0]] = close_stk[date_list_idx[0]]
        for c in range(1, len(date_list_idx)):
            if date_list_idx[c] in date_stk:
                fill_stk[date_list_idx[c]] = close_stk[date_list_idx[c]]
            else:
                fill_stk[date_list_idx[c]] = fill_stk[date_list_idx[c-1]]

        for d in date_stk:
            if d in date_list_idx:
                fill_stk.pop(d)


        for e in fill_stk:
            insert_sql = 'insert into data.' + table3 + ' values (' + symbol_list3 + ',\'' + str(e) +'\',\'' + str(float(fill_stk[e])) +'\',\'' + str(float(fill_stk[e])) +'\',\'' + str(float(fill_stk[e])) +'\',\'' + str(float(fill_stk[e])) + '\');'

            try:
                cur.execute(insert_sql)
            except Exception as e:
                print(e)

        log.info(symbol_list3 + 'is filled.')

def fill_stk(table):
    items2 = 'symbol, min(date), max(date)'
    table2 = table
    # table2 = 'stk_price'
    condition = ' group by symbol order by symbol'
    db_data2 = get_all_data(items2, table2, condition)

    for a in range(0, len(db_data2)):
    # for a in range(0, 1):
        index_start = date_list.index(db_data2[a][1])
        index_end = date_list.index(db_data2[a][2]) + 1
        date_list_idx = date_list[index_start:index_end]

        # item3 = 'date, close'
        item3 = 'date, close, mktcap, trade_mktcap '
        table3 = table2
        symbol_list3 = '\'' + db_data2[a][0] + '\''
        startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
        endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
        stk_data = get_data(item3, table3, symbol_list3, startDate3, endDate3)

        date_stk = []
        close_stk = {}
        mkt_stk = {}
        trade_mkt_stk = {}
        for b in range(0, len(stk_data)):
            date_stk.append(stk_data[b][0])
            close_stk[stk_data[b][0]] = stk_data[b][1]
            mkt_stk[stk_data[b][0]] = stk_data[b][2]
            trade_mkt_stk[stk_data[b][0]] = stk_data[b][3]

        fill_stk = {}
        fill_mkt_stk = {}
        fill_trade_mkt_stk = {}
        fill_stk[date_list_idx[0]] = close_stk[date_list_idx[0]]
        fill_mkt_stk[date_list_idx[0]] = mkt_stk[date_list_idx[0]]
        fill_trade_mkt_stk[date_list_idx[0]] = trade_mkt_stk[date_list_idx[0]]
        for c in range(1, len(date_list_idx)):
            if date_list_idx[c] in date_stk:
                fill_stk[date_list_idx[c]] = close_stk[date_list_idx[c]]
                fill_mkt_stk[date_list_idx[c]] = mkt_stk[date_list_idx[c]]
                fill_trade_mkt_stk[date_list_idx[c]] = trade_mkt_stk[date_list_idx[c]]
            else:
                log.info(date_list_idx[c])
                fill_stk[date_list_idx[c]] = fill_stk[date_list_idx[c - 1]]
                fill_mkt_stk[date_list_idx[c]] = fill_mkt_stk[date_list_idx[c - 1]]
                fill_trade_mkt_stk[date_list_idx[c]] = fill_trade_mkt_stk[date_list_idx[c - 1]]

        for d in date_stk:
            if d in date_list_idx:
                fill_stk.pop(d)
                fill_mkt_stk.pop(d)
                fill_trade_mkt_stk.pop(d)

        for e in fill_stk:
            insert_sql = 'insert into data.' + table3 + ' values (' + symbol_list3 + ',\'' + str(e) + '\',\'' + str(
                float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'' + str(
                float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'0\',\'0\',\'' + str(fill_mkt_stk[e]) +'\',\'' + str(fill_trade_mkt_stk[e])  + '\');'

            try:
                cur.execute(insert_sql)
            except Exception as e:
                print(e)

        log.info(symbol_list3 + 'is filled.')

def fill_ratio(table):
    item = 'symbol, min(date), max(date)'
    table = table
    condition = ' where symbol > \'600757.SH\' and date >= \'2010-01-01\' and date < \'2018-03-15\' group by symbol order by symbol'
    db_data = get_all_data(item, table, condition)

    for a in range(0, len(db_data)):
        index_start = date_list.index(db_data[a][1])
        index_end = date_list.index(db_data[a][2]) + 1
        date_list_idx = date_list[index_start:index_end]

        item2 = 'date, pe_ttm, pb'
        table2 = table
        symbol_list2 = '\'' + db_data[a][0] + '\''
        startDate2 = db_data[a][1].strftime('%Y-%m-%d')
        endDate2 = db_data[a][2].strftime('%Y-%m-%d')
        stk_data = get_data(item2, table2, symbol_list2, startDate2, endDate2)
        date_stk = []
        pe_ttm_stk = {}
        pb_stk = {}
        for b in range(0, len(stk_data)):
            date_stk.append(stk_data[b][0])
            pe_ttm_stk[stk_data[b][0]] = stk_data[b][1]
            pb_stk[stk_data[b][0]] = stk_data[b][2]

        fill_stk = {}
        fill_stk[date_list_idx[0]] = [float(pe_ttm_stk[date_list_idx[0]]),float(pb_stk[date_list_idx[0]])]
        for c in range(1, len(date_list_idx)):
            if date_list_idx[c] in date_stk:
                fill_stk[date_list_idx[c]] = [float(pe_ttm_stk[date_list_idx[c]]),float(pb_stk[date_list_idx[c]])]
            else:
                fill_stk[date_list_idx[c]] = fill_stk[date_list_idx[c-1]]

        for d in date_stk:
            if d in date_list_idx:
                fill_stk.pop(d)

        for e in fill_stk:
            insert_sql = 'insert into data.' + table2 + ' values (' + symbol_list2 + ',\'' + str(e) +'\',' + str(fill_stk[e]).replace('[','').replace(']','') + ');'

            try:
                cur.execute(insert_sql)
            except Exception as e:
                print(e)

        log.info(symbol_list2 + 'is filled.')

# fill_adj_stk('stk_price_forward')
# fill_adj_stk('stk_price_backward')
# fill_stk('stk_price')

fill_ratio('stk_ratio')

connClose(conn, cur)