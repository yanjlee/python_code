# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from CIGRG.WindPy import w
import logging as log
import datetime
from datetime import timedelta, datetime
import numpy as np
from ConnectDB import connDB, connClose, get_all_data, get_data
from gevent import monkey; monkey.patch_all()

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
    # w_data = w.wsd(symbol_list, "pe_ttm", '2018-04-11', '2018-04-12', "")
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
    # w_data2= w.wsd(symbol_list, "pb_lf", '2018-04-11', '2018-04-12', "")
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

update_stk_ratio()