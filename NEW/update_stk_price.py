# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
# from WindPy import w
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import logging as log
import datetime
import tushare as ts
from datetime import timedelta, datetime
from ConnectDB import connDB, connClose, get_all_data, get_data, fill_data
import os
import re
import urllib.request
import gevent
from gevent import monkey, pool; monkey.patch_all()
import pandas as pd

set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')
ts.set_token('c9c199c5d1f496ac02cca4dc086a6e7b1e36e0dc25630bc1cd7c621d')
pro = ts.pro_api()

# update stk_price
def update_stk_price():
    def download_price(url,symbol):
        local = 'C:/temp/stk_price/' + symbol[1:] + '.txt'
        try:
            urllib.request.urlretrieve(url, local)
            print(symbol[1:] + ' is downloaded.')
        except Exception as e:
            print(e)

    def roll_data():
        items = 'symbol, max(date) as date'
        table = 'stk_price'
        condition = ' group by symbol order by symbol'
        data_info = get_all_data(items, table, condition)
        stk_info = {}
        for stock in data_info:
            stk_info[stock[0]] = stock[1]
        enddate = datetime.now().date()
        urls = {}
        for k in stk_info:
            startdate = stk_info[k]
            if startdate > enddate:
                continue
            if k.startswith('6'):
                symbol = '0' + k.replace('.SH', '')
            else:
                symbol = '1' + k.replace('.SZ', '')
            urls[symbol] = 'http://quotes.money.163.com/service/chddata.html?code=' + symbol + '&start=' + startdate.strftime(
                '%Y%m%d') + '&end=' + enddate.strftime('%Y%m%d')
        p = pool.Pool(5)
        threads = [p.spawn(download_price, urls[key], key) for key in urls]
        gevent.joinall(threads)

    def format_files():
        roll_data()
        path = 'C:/temp/stk_price/'
        for filename in os.listdir(path):
            stockprice = open(path + filename, mode='r', encoding=None, errors=None, newline=None, closefd=True,
                              opener=None)
            content = stockprice.readlines()
            del content[0]
            for r in range(0, len(content)):
                if filename.startswith('6'):
                    content[r] = re.sub(r'\'(?P<name>\w+)', '\g<name>.SH', content[r]).strip()
                else:
                    content[r] = re.sub(r'\'(?P<name>\w+)', '\g<name>.SZ', content[r]).strip()
                list = content[r].split(',')

                del list[2]
                del list[6:8]
                del list[7]
                del list[8]
                del list[-1]
                line = str(list).replace('[', '(').replace(']', ')').replace('None', '0')
                content[r] = line
            stockprice.close()
            stockvalue = open(path + filename, mode='w+', encoding=None, errors=None, newline=None, closefd=True,
                              opener=None)
            for r2 in range(0, len(content)):
                stockvalue.writelines(content[r2] + '\n')
            stockvalue.close()

    def load_data_to_db():
        format_files()
        path = 'C:/temp/stk_price/'
        for filename in os.listdir(path):
            stock = open(path+filename, mode='r', encoding=None, errors=None, newline=None, closefd=True, opener=None)
            hisprice = stock.readlines()
            for j in range(0,len(hisprice)):
                istsql = 'insert into data.stk_price (date,symbol,close,high,low,open,chgrate,volume,mktcap,trade_mktcap) values '+ hisprice[j]
                # print(istsql)
                try:
                    fill_data(istsql)
                except Exception as e:
                    print(e)
                    print(istsql)
            print(filename + ' is loaded into database.')
            stock.close()
            try:
                os.remove(path + filename)
                print(filename + ' is deleted.')
            except Exception as e:
                print(e)
        print('''########################################''' +'\n' + ' data.stk_price is updated to latest status.' +'\n' + '''########################################''')

    def fill_stk_data():
        load_data_to_db()
        items = 'symbol, date'
        endDate = (datetime.now().date() + timedelta(days=-1)).strftime('%Y%m%d')
        startDate = (datetime.now().date() + timedelta(days=-5)).strftime('%Y%m%d')
        table = 'idx_price'
        symbol_list = ['000001.SH']
        db_data = get_data(items, table, symbol_list, startDate, endDate)

        date_list = []
        for i in range(0, len(db_data)):
            date_list.append(db_data[i][1])

        items2 = 'symbol, min(date), max(date)'
        table2 = 'stk_price'
        condition = ' where date >= \'' + startDate + '\' and date <=\'' + endDate + '\' group by symbol order by symbol'
        db_data2 = get_all_data(items2, table2, condition)

        for a in range(0, len(db_data2)):
            index_start = date_list.index(db_data2[a][1])
            index_end = date_list.index(db_data2[a][2]) + 1
            date_list_idx = date_list[index_start:index_end]

            item3 = 'date, close, mktcap, trade_mktcap '
            table3 = table2
            symbol_list3 = '\'' + db_data2[a][0] + '\''
            startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
            endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
            if startDate3 > endDate3:
                continue
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

            for d in date_list_idx:
                if d in date_stk:
                    fill_stk.pop(d)
                    fill_mkt_stk.pop(d)
                    fill_trade_mkt_stk.pop(d)

            for e in fill_stk:
                insert_sql = 'insert into data.' + table3 + ' values (' + symbol_list3 + ',\'' + str(e) + '\',\'' + str(
                    float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'' + str(
                    float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'0\',\'0\',\'' + str(
                    fill_mkt_stk[e]) + '\',\'' + str(fill_trade_mkt_stk[e]) + '\');'
                # print(insert_sql)
                try:
                    fill_data(insert_sql)
                except Exception as e:
                    print(e)
            print(symbol_list3 + 'is filled.')
        fill_stk_data()


# update forward/backward stock price
def update_adj_price(table, type):

    def fill_adj_stk(table):
        items = 'symbol, date'
        endDate = (datetime.now().date() + timedelta(days=-1)).strftime('%Y%m%d')
        startDate = (datetime.now().date() + timedelta(days=-5)).strftime('%Y%m%d')
        tables = 'idx_price'
        symbol_list = ['000001.SH']
        db_data = get_data(items, tables, symbol_list, startDate, endDate)

        date_list = []
        for i in range(0, len(db_data)):
            date_list.append(db_data[i][1])

        items2 = 'symbol, min(date), max(date)'
        table2 = table
        condition = ' where date >= \'' + startDate + '\' and date <=\'' + endDate + '\' group by symbol order by symbol'
        db_data2 = get_all_data(items2, table2, condition)
        for a in range(0, len(db_data2)):
            index_start = date_list.index(db_data2[a][1])
            index_end = date_list.index(db_data2[a][2])
            if index_start >= index_end:
                continue
            date_list_idx = date_list[index_start:index_end]

            item3 = 'date, close'
            table3 = table2
            symbol_list3 = '\'' + db_data2[a][0] + '\''
            startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
            endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
            if startDate3 > endDate3:
                continue
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
                    fill_stk[date_list_idx[c]] = fill_stk[date_list_idx[c - 1]]

            for d in date_stk:
                if d in date_list_idx:
                    fill_stk.pop(d)

            for e in fill_stk:
                insert_sql = 'insert into data.' + table3 + ' values (' + symbol_list3 + ',\'' + str(e) + '\',\'' + str(
                    float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'' + str(
                    float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\');'

                try:
                    fill_data(insert_sql)
                except Exception as e:
                    print(e)
            print(symbol_list3 + 'is filled.')

    items = 'symbol, max(date) as date'
    tables = table
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    edate = datetime.now().date().strftime('%Y-%m-%d')

    for k in range(0, len(data_info)):
        sdate = (data_info[k][1] + timedelta(1)).strftime('%Y-%m-%d')
        if sdate > edate:
           continue
        try:
            pricedata = ts.get_k_data(data_info[k][0].replace('.SH','').replace('.SZ',''), ktype='D', autype=type, start=sdate, end=edate);
            del pricedata['volume']
        except Exception as e:
            print(e)

        for h in range(0, len(pricedata)):
            if data_info[k][0].startswith('6'):
                values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SH\'')
            else:
                values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SZ\'')
            insql = 'insert into data.' + table + ' (date,open,close,high,low,symbol) values (' + values + ');'
            # print(insql)
            try:
                fill_data(insql)
            except Exception as e:
                print(e)

        print(str(data_info[k][0]) + ' is inserted' )
    fill_adj_stk(table)


def update_stk_price_gm():
    items = 'symbol, max(date) as date'
    table = 'stk_price'
    condition = ' group by symbol order by symbol'
    date_info = dict(get_all_data(items, table, condition))
    edate = datetime.now().date().strftime('%Y-%m-%d')
    for symbol, v in date_info.items():
        if symbol.startswith('6'):
            sym = 'SHSE.' + symbol.replace('.SH', '')
        else:
            sym = 'SZSE.' + symbol.replace('.SZ', '')
        sdate = v.strftime('%Y-%m-%d')
        stk_data1 = history(symbol=sym, frequency='1d', start_time = sdate, end_time = edate, fields='open,high,low,close,volume,bob',fill_missing='Last',adjust=0, df = 'True')
        if len(stk_data1) == 0:
            continue
        stk_data2 = get_fundamentals(table='trading_derivative_indicator', symbols=sym, start_date=sdate, end_date=edate,fields='TOTMKTCAP, NEGOTIABLEMV', df = 'True')
        stk_data = pd.concat([stk_data1, stk_data2], axis = 1)
        stk_data['chg_rate'] = (stk_data.close - stk_data.close.shift(1))/stk_data.close.shift(1)
        stk_data = stk_data.dropna()
        try:
            stk_data = stk_data.drop(['pub_date','end_date','symbol'],axis = 1)
        except Exception as e:
            pass
        stk_data = stk_data.round(4)

        for i in range(0, len(stk_data)):
            insert_str = 'insert into data.stk_price(symbol,date,close,high,low,open,volume,mktcap,trade_mktcap,chgrate) values(\'' + symbol + '\',' + str(list(stk_data.iloc[i])).replace('[Timestamp(','').replace(')','').replace(']',')')
            try:
                fill_data(insert_str)
            except Exception as e:
                print(e)
                print(insert_str)
        print(symbol + ' : price is updated from GM' )
################################

update_stk_price()
update_adj_price('stk_price_forward', 'qfq')
update_adj_price('stk_price_backward', 'hfq')
update_stk_price_gm()
