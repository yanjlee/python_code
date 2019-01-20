# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from WindPy import w
import logging as log
import datetime
from datetime import timedelta, datetime
import pandas as pd
from ConnectDB import connDB, connClose, get_all_data, get_data, fill_data
import os
import re
import urllib.request
import gevent
from gevent import monkey, pool; monkey.patch_all()


def update_idx_price():

    def download_price(url, symbol):
        local = 'C:/temp/idx_price/' + symbol[1:] + '.txt'
        try:
            urllib.request.urlretrieve(url, local)
            print(symbol[1:] + ' is downloaded.')
        except Exception as e:
            print(e)

    def get_data():
        items = 'symbol, max(date) as date'
        table = 'idx_price'
        condition = ' where symbol not like \'%.WI\' group by symbol order by symbol'
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
            if k.startswith('0') or k.startswith('9'):
                symbol = '0' + k.replace('.SH', '')
            else:
                symbol = '1' + k.replace('.SZ', '')
            urls[symbol] = 'http://quotes.money.163.com/service/chddata.html?code=' + symbol + '&start=' + startdate.strftime(
                '%Y%m%d') + '&end=' + enddate.strftime('%Y%m%d')
        p = pool.Pool(5)
        threads = [p.spawn(download_price, urls[key], key) for key in urls]
        gevent.joinall(threads)


    def format_files():
        get_data()
        path = 'C:/temp/idx_price/'
        for filename in os.listdir(path):
            stockprice = open(path + filename, mode='r', encoding=None, errors=None, newline=None, closefd=True,
                              opener=None)
            content = stockprice.readlines()
            del content[0]
            for r in range(0, len(content)):
                if filename.startswith('0') or filename.startswith('9'):
                    content[r] = re.sub(r'\'(?P<name>\w+)', '\g<name>.SH', content[r]).strip()
                else:
                    content[r] = re.sub(r'\'(?P<name>\w+)', '\g<name>.SZ', content[r]).strip()
                list = content[r].split(',')

                del list[2]
                del list[6:8]
                del list[7:9]
                del list[8:]
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
        path = 'C:/temp/idx_price/'
        conn,cur = connDB()
        for filename in os.listdir(path):
            stock = open(path+filename, mode='r', encoding=None, errors=None, newline=None, closefd=True, opener=None)
            hisprice = stock.readlines()
            for j in range(0,len(hisprice)):
                istsql = 'insert into data.idx_price (date,symbol,close,high,low,open,chgrate,trade) values '+ hisprice[j]
                # print(istsql)
                try:
                    conn.cursor().execute(istsql)
                except Exception as e:
                    print(e)
                    print(istsql)
            conn.commit();
            log.info(filename + ' is loaded into database.')
            stock.close()
            try:
                os.remove(path + filename)
                print(filename + ' is deleted.')
            except Exception as e:
                print(e)
        connClose(conn, cur)
        log.info('''########################################''' +'\n' + ' data.idx_price is updated to latest status.' +'\n' + '''########################################''')

    load_data_to_db()

# update w_idx price data
def update_w_idx_price():
    w.start()
    conn, cur = connDB()
    items = 'symbol, max(date) as date'
    tables = 'idx_price'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    w_idx_data = dict(data_info)
    end_date = datetime.now().date().strftime('%Y-%m-%d')
    for i in w_idx_data:
        start_date = (w_idx_data[i]+timedelta(1)).strftime('%Y-%m-%d')
        if start_date > end_date:
            continue
        w_data = w.wsd(i, "open,high,low,close,pct_chg,amt", start_date, end_date, "")
        # if len(w_data.Data) <= 1 or w_data.Data[0][1] == None:
        #     continue

        for s in range(0, len(w_data.Times)):
            temp = []
            temp.append(i)
            temp.append(w_data.Times[s].strftime('%Y-%m-%d'))
            for r in range(0, len(w_data.Fields)):
                temp.append(w_data.Data[r][s])
            insert_sql = 'insert into data.idx_price values(' + str(temp).replace('[', '').replace(']', '') + ');'
            # print(insert_sql)
            try:
                conn.cursor().execute(insert_sql)
            except Exception as e:
                print(e)
        print(i + ' is inserted. ')
        conn.commit()
    connClose(conn, cur)




update_idx_price()
update_w_idx_price()
