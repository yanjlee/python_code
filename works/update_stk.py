# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from CIGRG.WindPy import w
import logging as log
import datetime
import tushare as ts
from datetime import timedelta, datetime
import numpy as np
import pandas as pd
from ConnectDB import connDB, connClose, get_all_data, get_data, fill_data
import os
import re
import urllib.request
import gevent
from gevent import monkey, pool; monkey.patch_all()


# update stk_price
def update_stk_price():
    def download_price(url,symbol):
        local = 'D:/temp/stk_price/' + symbol[1:] + '.txt'
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
        path = 'D:/temp/stk_price/'
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
        path = 'D:/temp/stk_price/'
        conn,cur = connDB()
        for filename in os.listdir(path):
            stock = open(path+filename, mode='r', encoding=None, errors=None, newline=None, closefd=True, opener=None)
            hisprice = stock.readlines()
            for j in range(0,len(hisprice)):
                istsql = 'insert into data.stk_price (date,symbol,close,high,low,open,chgrate,volume,mktcap,trade_mktcap) values '+ hisprice[j]
                # print(istsql)
                try:
                    conn.cursor().execute(istsql)
                except Exception as e:
                    print(e)
                    print(istsql)
            conn.commit();
            print(filename + ' is loaded into database.')
            stock.close()
            try:
                os.remove(path + filename)
                print(filename + ' is deleted.')
            except Exception as e:
                print(e)
        connClose(conn, cur)
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
        conn, cur = connDB()

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
                    cur.execute(insert_sql)
                except Exception as e:
                    print(e)
            conn.commit();
            log.info(symbol_list3 + 'is filled.')

        connClose(conn, cur)

    fill_stk_data()

def update_stk_price_2():
    w.start()
    conn, cur = connDB()
    items = 'symbol, max(date) as date'
    tables = 'stk_price'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    stk_data = dict(data_info)
    end_date = datetime.now().date().strftime('%Y-%m-%d')
    for i in stk_data:
        start_date = (stk_data[i] + timedelta(1)).strftime('%Y-%m-%d')
        if start_date > end_date:
            continue
        w_data = w.wsd(i, "open,high,low,close,pct_chg,volume,mkt_cap_float,mkt_cap_ashare", start_date, end_date,
                       "unit=1;currencyType=")
        if len(w_data.Data) <= 1:# or w_data.Data[0][1] == None:
            continue

        for s in range(0, len(w_data.Times)):
            temp = []
            temp.append(i)
            temp.append(w_data.Times[s].strftime('%Y-%m-%d'))
            for r in range(0, len(w_data.Fields)):
                temp.append(w_data.Data[r][s])
            insert_sql = 'insert into data.stk_price values(' + str(temp).replace('[', '').replace(']', '') + ');'
            # print(insert_sql)
            try:
                conn.cursor().execute(insert_sql)
            except Exception as e:
                print(e)
            print(i + ' is inserted. ')
            conn.commit()
    connClose(conn, cur)

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
        conn, cur = connDB()

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
                    cur.execute(insert_sql)
                except Exception as e:
                    print(e)
            conn.commit()
            print(symbol_list3 + 'is filled.')

    conn, cur = connDB()
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
                conn.cursor().execute(insql)
            except Exception as e:
                print(e)

        conn.commit()
        log.info(str(data_info[k][0]) + ' is inserted' )

    fill_adj_stk(table)
    connClose(conn, cur)

def update_stk_fina_calc():
    conn, cur = connDB()
    request_date = datetime.now().date().strftime('%Y%m%d')
    items = 'symbol, max(date) as date'
    tables = 'stk_fina_calc'
    condition = ' where (rpt_date is not null and eps_ttm is not null and roe_ttm is not null and div_yield is not null) group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    update_info = {}
    for i in data_info:
        update_info[i[0]] = i[1].strftime('%Y-%m-%d')
    symbol_list = list(update_info.keys())
    # symbol_list2 = ['002456.SZ','000001.SZ','601318.SH']

    w.start()
    w_data = w.wsd(symbol_list, "stm_predict_issuingdate", "ED-5M", request_date, "rptYear=2016;Period=Q;Days=Alldays")
    report_info = []
    for s in range(0, len(w_data.Codes)):
        for r in range(0, len(w_data.Times)):
            report_info_temp = []
            if w_data.Data[s][r] == None or w_data.Data[s][r].strftime('%Y-%m-%d') > request_date:
                continue
            report_info_temp.append(w_data.Codes[s])
            report_info_temp.append(w_data.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data.Data[s][r].strftime('%Y-%m-%d'))
            report_info.append(report_info_temp)

    for k in report_info:
        insert_sql = 'insert into data.stk_fina_calc(symbol, date,rpt_date) values(' + str(k).replace('[', '').replace(']',
                                                                                                          '') + ');'
        insert_sql = insert_sql.replace('nan', 'default')
        update_sql = 'update data.stk_fina_calc set rpt_date = \'' + k[2] + '\' where symbol = \'' + k[0] + '\' and date = \'' + k[1]+ '\''
        update_sql = update_sql.replace('\'nan\'', 'default')
        try:
            cur.execute(insert_sql)
        except Exception as e:
            print(e)
        try:
            cur.execute(update_sql)
        except Exception as e:
            print(e)
        conn.commit()

    request_list = []
    for t in range(0, len(report_info)):
        request_list.append(report_info[t][0])
    request_list = list(set(request_list))
    # request_list2 = ['000001.SZ','601318.SH']
    w_data2 = w.wsd(request_list, "eps_ttm", "ED-5M", request_date, "rptYear=2016;Period=Q;Days=Alldays")
    eps_info = []
    for s in range(0, len(w_data2.Codes)):
        for r in range(0, 2):
            report_info_temp = []
            if w_data2.Data[s][r] == None or (w_data2.Times[r].strftime('%Y-%m-%d')[5:] != '12-31' and w_data2.Times[r].strftime('%Y-%m-%d')[5:] != '03-31' and w_data2.Times[r].strftime('%Y-%m-%d')[5:] != '06-31' and w_data2.Times[r].strftime('%Y-%m-%d')[5:] != '09-30') or np.isnan(w_data2.Data[s][r]):
                continue
            report_info_temp.append(w_data2.Codes[s])
            report_info_temp.append(w_data2.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data2.Data[s][r])
            eps_info.append(report_info_temp)

    for j in eps_info:
        update_sql = 'update data.stk_fina_calc set eps_ttm = \'' + str(j[2]) + '\' where symbol = \'' + j[0] + '\' and date = \'' + j[1] + '\''
        update_sql = update_sql.replace('\'nan\'', 'default')
        try:
            cur.execute(update_sql)
        except Exception as e:
            print(e)
    conn.commit()


    w_data3 = w.wsd(request_list, "roe_ttm2", "ED-5M", request_date, "rptYear=2016;Period=Q;Days=Alldays")
    roe_info = []
    for s in range(0, len(w_data3.Codes)):
        for r in range(0, 2):
            report_info_temp = []
            if w_data3.Data[s][r] == None or (
                    w_data3.Times[r].strftime('%Y-%m-%d')[5:] != '12-31' and w_data3.Times[r].strftime('%Y-%m-%d')[
                                                                             5:] != '03-31' and w_data3.Times[
                                                                                                    r].strftime(
                    '%Y-%m-%d')[5:] != '06-31' and w_data3.Times[r].strftime('%Y-%m-%d')[5:] != '09-30') or np.isnan(w_data3.Data[s][r]):
                continue
            report_info_temp.append(w_data3.Codes[s])
            report_info_temp.append(w_data3.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data3.Data[s][r])
            roe_info.append(report_info_temp)

    for g in roe_info:
        update_sql = 'update data.stk_fina_calc set roe_ttm = \'' + str(g[2]) + '\' where symbol = \'' + g[0] + '\' and date = \'' + g[1] + '\''
        update_sql = update_sql.replace('\'nan\'', 'default')
        try:
            cur.execute(update_sql)
        except Exception as e:
            print(e)
    conn.commit()

    w_data4 = w.wsd(request_list, "dividendyield2", "ED-5M", request_date, "rptYear=2016;Period=Q;Days=Alldays")
    div_info = []
    for s in range(0, len(w_data4.Codes)):
        for r in range(0, 2):
            report_info_temp = []
            if w_data4.Data[s][r] == None or (
                    w_data4.Times[r].strftime('%Y-%m-%d')[5:] != '12-31' and w_data4.Times[r].strftime('%Y-%m-%d')[
                                                                             5:] != '03-31' and w_data4.Times[
                                                                                                    r].strftime(
                    '%Y-%m-%d')[5:] != '06-31' and w_data4.Times[r].strftime('%Y-%m-%d')[5:] != '09-30') or np.isnan(w_data4.Data[s][r]):
                continue
            report_info_temp.append(w_data4.Codes[s])
            report_info_temp.append(w_data4.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data4.Data[s][r])
            div_info.append(report_info_temp)

    for f in div_info:
        update_sql = 'update data.stk_fina_calc set div_yield = \'' + str(f[2]) + '\' where symbol = \'' + f[0] + '\' and date = \'' + f[1] + '\''
        update_sql = update_sql.replace('\'nan\'', 'default')
        try:
            cur.execute(update_sql)
        except Exception as e:
            print(e)
    conn.commit()

    w_data5 = w.wsd(request_list, "roic_ttm", "ED-5M", request_date, "Period=Q;Days=Alldays")
    for s in range(0, len(w_data5.Codes)):
        for r in range(0, len(w_data5.Times)):
            if np.isnan(w_data5.Data[s][r]):
                continue
            update_sql = 'update data.stk_fina_calc set roic_ttm =\'' + str(w_data5.Data[s][r]) + '\' where symbol =\'' + \
                         w_data5.Codes[s] + '\' and date = \'' + w_data5.Times[r].strftime('%Y-%m-%d') + '\';'
            try:
                conn.cursor().execute(update_sql)
            except Exception as e:
                print(e)

            conn.commit()

    log.info('stk_fina_calc is updated.')

    connClose(conn, cur)

def update_stk_ratio():
    conn, cur = connDB()
    request_date = datetime.now().date().strftime('%Y-%m-%d')
    items = 'symbol'
    tables = 'stk_ratio'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    symbol_list = []
    for i in data_info:
        symbol_list.append(i[0])

    w.start()
    w_data = w.wsd(symbol_list, "pe_ttm", "ED-1TD", request_date, "")  # "ED-1TD"
    # w_data = w.wsd(symbol_list, "pe_ttm", '2018-04-02', '2018-04-02', "")
    pe_info = []
    for s in range(0, len(w_data.Codes)):
        for r in range(0, len(w_data.Times)):
            report_info_temp = []
            if np.isnan(w_data.Data[s][r]):
                continue
            report_info_temp.append(w_data.Codes[s])
            report_info_temp.append(w_data.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data.Data[s][r])
            pe_info.append(report_info_temp)

    w_data2 = w.wsd(symbol_list, "pb_lf", "ED-1TD", request_date, "")  # "ED-1TD"
    pb_info = []
    for s in range(0, len(w_data2.Codes)):
        for r in range(0, len(w_data2.Times)):
            report_info_temp = []
            if np.isnan(w_data2.Data[s][r]):
                continue
            report_info_temp.append(w_data2.Codes[s])
            report_info_temp.append(w_data2.Times[r].strftime('%Y-%m-%d'))
            report_info_temp.append(w_data2.Data[s][r])
            pb_info.append(report_info_temp)

    for k in pb_info:
        insert_sql = 'insert into data.stk_ratio (symbol, date, pb) values (' + str(k).replace('[', '').replace(']',
                                                                                                          '') + ');'
        try:
            cur.execute(insert_sql)
        except Exception as e:
            print(e)
    conn.commit()

    for j in pe_info:
        update_sql = 'update data.stk_ratio set pe_ttm = \'' + str(j[2]) + '\' where symbol = \'' + j[
            0] + '\' and date = \'' + j[1] + '\';'
        try:
            cur.execute(update_sql)
        except Exception as e:
            print(e)

    conn.commit()
    connClose(conn, cur)
    log.info('stk_ratio is updated.')

    def fill_ratio_data():
        conn, cur = connDB()

        items = 'symbol, date'
        endDate = (datetime.now().date() + timedelta(days=-1)).strftime('%Y%m%d')
        startDate = (datetime.now().date() + timedelta(days=-15)).strftime('%Y%m%d')
        table = 'idx_price'
        symbol_list = ['000001.SH']
        db_data = get_data(items, table, symbol_list, startDate, endDate)

        date_list = []
        for i in range(0, len(db_data)):
            date_list.append(db_data[i][1])
        conn, cur = connDB()

        items2 = 'symbol, min(date), max(date)'
        table2 = 'stk_ratio'
        condition = ' where date >= \'' + startDate + '\' and date <=\'' + endDate + '\' group by symbol order by symbol'
        db_data2 = get_all_data(items2, table2, condition)

        for a in range(0, len(db_data2)):
            index_start = date_list.index(db_data2[a][1])
            index_end = date_list.index(db_data2[a][2]) + 1
            date_list_idx = date_list[index_start:index_end]

            item3 = 'date, pe_ttm, pb '
            table3 = table2
            symbol_list3 = '\'' + db_data2[a][0] + '\''
            startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
            endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
            if startDate3 > endDate3:
                continue
            stk_data = get_data(item3, table3, symbol_list3, startDate3, endDate3)

            date_stk = []
            pe_stk = {}
            pb_stk = {}
            for b in range(0, len(stk_data)):
                date_stk.append(stk_data[b][0])
                pe_stk[stk_data[b][0]] = stk_data[b][1]
                pb_stk[stk_data[b][0]] = stk_data[b][2]

            fill_pe_stk = {}
            fill_pb_stk = {}
            fill_pe_stk[date_list_idx[0]] = pe_stk[date_list_idx[0]]
            fill_pb_stk[date_list_idx[0]] = pb_stk[date_list_idx[0]]
            for c in range(1, len(date_list_idx)):
                if date_list_idx[c] in date_stk:
                    fill_pe_stk[date_list_idx[c]] = pe_stk[date_list_idx[c]]
                    fill_pb_stk[date_list_idx[c]] = pb_stk[date_list_idx[c]]
                else:
                    fill_pe_stk[date_list_idx[c]] = fill_pe_stk[date_list_idx[c - 1]]
                    fill_pb_stk[date_list_idx[c]] = fill_pb_stk[date_list_idx[c - 1]]

            for d in date_list_idx:
                if d in date_stk:
                    date_stk.remove(d)
                    fill_pe_stk.pop(d)
                    fill_pb_stk.pop(d)
            if len(date_stk) == 0:
                continue
            for e in date_stk:
                insert_sql = 'insert into data.' + table3 + ' values (' + symbol_list3 + ',\'' + str(e) + '\',\'' + str(
                    float(fill_pe_stk[e])) + '\',\'' + str(float(fill_pb_stk[e])) + '\');'
                print(insert_sql)
                try:
                    cur.execute(insert_sql)
                except Exception as e:
                    print(e)
            conn.commit();
            log.info(symbol_list3 + 'is filled.')

        connClose(conn, cur)
    fill_ratio_data()


def update_stk_adj_factor():
    w.start()
    conn, cur = connDB()
    items = 'symbol, max(date)'
    tables = 'stk_adj_factor'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    stk_data = dict(data_info)
    end_date = datetime.now().date().strftime('%Y-%m-%d')

    for i in stk_data:
        start_date = (stk_data[i] + timedelta(1)).strftime('%Y-%m-%d')
        if start_date > end_date:
            continue
        w_data = w.wsd(i, "adjfactor", start_date, end_date, "")

        for s in range(0, len(w_data.Times)):
            insert_sql = 'insert into data.stk_adj_factor values(\'' + i + '\', \'' + w_data.Times[s].strftime(
                '%Y-%m-%d') + '\',\'' + str(w_data.Data[0][s]) + '\');'
            # print(insert_sql)
            try:
                conn.cursor().execute(insert_sql)
            except Exception as e:
                print(e)
        print(i + ' is inserted in stk_adj_factor. ')
        conn.commit()
    connClose(conn, cur)


def update_stk_price_tec():

    def calc_ema(j):
        items = 'date, close'
        table = 'stk_price_forward'
        condition = ' where symbol = \'' + j + '\' order by date desc limit 250'
        idx_data = get_all_data(items, table, condition)
        idx_price = dict(idx_data)
        df_price = pd.DataFrame(list(idx_price.values()), columns=['close'], index=idx_price.keys())
        df_price.sort_index(inplace=True)

        ma_list = [5, 10, 21, 40, 60]
        for ma in ma_list:
            df_price['ema' + str(ma)] = df_price['close'].ewm(span=ma, min_periods=0, adjust=True,
                                                              ignore_na=False).mean()
        df_price = df_price.drop(columns=['close'])
        for h in range(0, len(df_price)):
            insert_sql = 'insert into data.stk_price_tec values(\'' + j + '\',\'' + df_price.index[h].strftime(
                '%Y-%m-%d') + '\', ' + str(list(df_price.iloc[h])).replace('[', '').replace(']', '') + ', default, default);'
            fill_data(insert_sql)

        print(j + ' is inserted')

    def calc_atr(j):
        # for j in symbols:
        items = 'date, high, low, close'
        table = 'stk_price_forward'
        condition = ' where symbol=\'' + j + '\'  order by date desc limit 200'
        stk_data = get_all_data(items, table, condition)
        date_list = []
        high = []
        low = []
        close = []
        for i in stk_data:
            date_list.append(i[0].strftime('%Y-%m-%d'))
            high.append(i[1])
            low.append(i[2])
            close.append(i[3])
        df = pd.DataFrame({'high': high, 'low': low, 'close': close}, index=date_list)
        df.sort_index(inplace=True)

        # Average True Range
        n = 13
        i = 0
        TR_l = [0]
        while i < len(df.index) - 1:
            TR = max(df['high'].iloc[i + 1], df['close'].iloc[i]) - min(df['low'].iloc[i + 1], df['close'].iloc[i])
            TR_l.append(TR)
            i = i + 1
        TR_s = pd.DataFrame(TR_l, columns=['TR'], index=df.index)
        # ATR = pd.Series(pd.ewma(TR_s, span=n, min_periods=n), name='ATR_' + str(n))
        df['atr' + str(n)] = TR_s['TR'].ewm(span=n, min_periods=0, adjust=True, ignore_na=False).mean()
        df['atr' + str(n + 8)] = TR_s['TR'].ewm(span=n + 7, min_periods=0, adjust=True, ignore_na=False).mean()

        # df = df.join(ATR)
        for h in range(len(df) - 5, len(df)):
            insert_sql = 'update data.stk_price_tec set atr13 =\'' + str(df['atr13'].iloc[h]) + '\' , atr21 = \'' + str(
                df['atr21'].iloc[h]) + '\' where symbol =\'' + j + '\' and date = \'' + df.index[h] + '\';'
            fill_data(insert_sql)
        print(j + '\'s ATR data are updated.')

    items = 'symbol'
    table = 'stk_price_forward'
    condition = ' group by symbol order by symbol'
    idx_data = get_all_data(items, table, condition)
    symbols = []
    for i in idx_data:
        symbols.append(i[0])

    for j in symbols:
        calc_ema(j)
        calc_atr(j)

    # pool = Pool(processes=1)
    # pool.map(calc_ema, symbols)
    # pool.map(calc_atr, symbols)
    # pool.close()
    # pool.join()

def fill_suspend_stk_data():


    items = 'date'
    table = 'idx_price'
    condition = ' where symbol= \'000001.SH\' and date > \'2015-01-02\' order by date asc'
    idx_date = get_all_data(items, table, condition)
    date_list = []
    for j in idx_date:
        date_list.append(j[0])

    w.start()
    request_date = date_list[-1].strftime('%Y-%m-%d')
    set_info = 'startdate=' + request_date + ';enddate=' + request_date + ';field=wind_code'
    suspend_symbols = w.wset("tradesuspend",set_info)
    symbols = suspend_symbols.Data[0]

    def fill_suspend_data_bf(tables):
        for i in symbols:
            if i.startswith('0') or i.startswith('3') or i.startswith('6'):
                items = 'date, close'
                table = tables
                condition = ' where symbol=\'' + i + '\'  order by date desc limit 1'
                stk_data = get_all_data(items, table, condition)
                if len(stk_data) == 0  or stk_data[0][0] >= datetime.now().date():
                    continue
                stk_date_list = date_list[date_list.index(stk_data[0][0]) + 1 :]
                for k in stk_date_list:
                    insert_sql = 'insert into data.' + tables + ' values(\'' + i + '\',\'' + k.strftime('%Y-%m-%d') + '\',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ');'
                    # print(insert_sql)
                    fill_data(insert_sql)
            print(i + '\'s data are updated.')

    def fill_suspend_data(tables):
        for i in symbols:
            if i.startswith('0') or i.startswith('3') or i.startswith('6'):
                items = 'date, close, mktcap,trade_mktcap'
                table = tables
                condition = ' where symbol=\'' + i + '\'  order by date desc limit 1'
                stk_data = get_all_data(items, table, condition)
                if len(stk_data) == 0  or stk_data[0][0] >= datetime.now().date():
                    continue
                stk_date_list = date_list[date_list.index(stk_data[0][0]) + 1 :]
                for k in stk_date_list:
                    insert_sql = 'insert into data.' + tables + ' values(\'' + i + '\',\'' + k.strftime('%Y-%m-%d') + '\',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ',' + str(float(stk_data[0][1])) + ',0,0,' + str(float(stk_data[0][2])) + ',' + str(float(stk_data[0][2])) + ');'
                    # print(insert_sql)
                    fill_data(insert_sql)
            print(i + '\'s data are updated.')

    # tbs = ['stk_price_forward', 'stk_price_backward']
    fill_suspend_data_bf('stk_price_forward')
    fill_suspend_data_bf('stk_price_backward')
    fill_suspend_data('stk_price')


################################

update_stk_price()
update_stk_price_2()
update_adj_price('stk_price_forward', 'qfq')
update_adj_price('stk_price_backward', 'hfq')
update_stk_fina_calc()
update_stk_ratio()
update_stk_adj_factor()
update_stk_price_tec()
fill_suspend_stk_data()