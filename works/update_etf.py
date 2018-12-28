# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=


import logging as log
import datetime
import tushare as ts
from datetime import timedelta, datetime
from ConnectDB import connDB, connClose, get_all_data
from gevent import monkey, pool; monkey.patch_all()

def update_etf_price():
    conn, cur = connDB()
    items = 'symbol, max(date) as date'
    tables = 'etf_price'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    end = datetime.now().date().strftime('%Y-%m-%d')
    for k in range(0, len(data_info)):
        start = (data_info[k][1] + timedelta(days=1)).strftime('%Y-%m-%d')
        if start > end:
            continue
        pricedata = ts.get_k_data(data_info[k][0].replace('.OF', ''), ktype='D', start=start, end=end)
        for h in range(0, len(pricedata)):
            values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.OF\'')
            insql = 'insert into data.etf_price (date,open,close,high,low,volume,symbol) values (' + values + ');'
            # print(insql)
            try:
                conn.cursor().execute(insql)
            except Exception as e:
                print(e)
        conn.commit()
        log.info(str(data_info[k][0]) + ' is inserted in etf_price')
    connClose(conn, cur)

# def update_etf_price_backward():
#     conn, cur = connDB()
#     items = 'symbol,  max(date) as date'
#     tables = 'etf_price_backward'
#     condition = ' group by symbol order by symbol'
#     data_info = get_all_data(items, tables, condition)
#     etf_info = dict(data_info)
#     end_date = datetime.now().strftime('%Y-%m-%d')
#     w.start()
#     for i in etf_info:
#         start_date = (etf_info[i] + timedelta(1)).strftime('%Y-%m-%d')
#         if start_date > end_date:
#             continue
#         etf_price = w.wsd(i, "close,pct_chg", start_date, end_date, "PriceAdj=B")
#         for r in range(0, len(etf_price.Times)):
#             etf_value = tuple([etf_price.Codes[0], etf_price.Times[r].strftime('%Y-%m-%d'), etf_price.Data[0][r],
#                                etf_price.Data[1][r]])
#             insert_sql = 'insert into data.etf_price_backward values ' + str(etf_value)
#             try:
#                 conn.cursor().execute(insert_sql)
#             except Exception as e:
#                 print(e)
#
#             update_sql = 'update data.etf_price_backward set close =\'' + str(etf_price.Data[0][r]) + '\', chg_rate = \'' + str(etf_price.Data[1][r]) + '\' where symbol = \'' + etf_price.Codes[0] + '\' and date = \'' + str(etf_price.Times[r]) + '\''
#             try:
#                 conn.cursor().execute(update_sql)
#             except Exception as e:
#                 print(e)
#
#         print(i + ' is inserted in etf_price_backward. ')
#         conn.commit()
#     connClose(conn, cur)

update_etf_price()
