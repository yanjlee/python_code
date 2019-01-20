# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta, datetime
from ConnectDB import get_all_data, get_data, fill_data
import tushare as ts

set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')
ts.set_token('c9c199c5d1f496ac02cca4dc086a6e7b1e36e0dc25630bc1cd7c621d')
pro = ts.pro_api()


def update_stk_adj_factor():
    current_data = get_instruments(exchanges=['SHSE', 'SZSE'], sec_types=[1], fields='symbol,trade_date,adj_factor',df=False)
    for i in current_data:
        symbol = i['symbol']
        if symbol.startswith('SHSE'):
            symbol = symbol.replace('SHSE.', '') + '.SH'
        else:
            symbol = symbol.replace('SZSE.', '') + '.SZ'
        insert_cd = 'insert into data.stk_adj_factor values(\'' + symbol + '\',\'' + i['trade_date'].strftime('%Y-%m-%d') + '\',' + str(round(i['adj_factor'],6)) + ');'
        try:
            fill_data(insert_cd)
        except Exception as e:
            print(e)

    items = 'symbol, max(date)'
    tables = 'stk_adj_factor'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    stk_data = dict(data_info)
    end_date = datetime.now().date().strftime('%Y%m%d')

    for j in stk_data:
        start_date = (stk_data[j] + timedelta(1)).strftime('%Y%m%d')
        if start_date > end_date:
            continue
        if j.startswith('6'):
            sym = 'SHSE.' + j.replace('.SH', '')
        else:
            sym = 'SZSE.' + j.replace('.SZ', '')
        gm_data = get_history_instruments(symbols=[sym], fields='symbol,trade_date,adj_factor', start_date=start_date,end_date=end_date, df=True)
        if len(gm_data)  == 0:
            continue
        for k in range(0, len(gm_data)):
            insert_gm = 'insert into data.stk_adj_factor values(\'' + j + '\',\'' + gm_data['trade_date'][k].strftime('%Y-%m-%d') + '\',' + str(round(gm_data['adj_factor'][k], 6)) + ');'
            try:
                fill_data(insert_gm)
            except Exception as e:
                print(e)
        # df = pro.adj_factor(ts_code=i, start_date=start_date, end_date=end_date)  # trade_date='2018-08-10')
        # for s in range(0, len(df)):
        #     insert_sql = 'insert into data.stk_adj_factor values(' + str(list(df.iloc[s])).replace('[','').replace(']','') + ');'
        #     # print(insert_sql)
        #     try:
        #         fill_data(insert_sql)
        #     except Exception as e:
        #         print(e)
        print(j + ' is inserted in stk_adj_factor. ')

def update_stk_PEPB():
    end_date = datetime.now().date().strftime('%Y-%m-%d')
    items = 'symbol, max(date)'
    tables = 'stk_ratio'
    condition = ' group by symbol order by symbol'
    data_info = get_all_data(items, tables, condition)
    ratio_data = dict(data_info)
    for key in ratio_data:
        if key.startswith('6'):
            sym = 'SHSE.' + key.replace('.SH','')
        else:
            sym = 'SZSE.' + key.replace('.SZ', '')
        start_date = (ratio_data[key] + timedelta(1)).strftime('%Y-%m-%d')
        if start_date > end_date:
            continue
        df_r = get_fundamentals(table='trading_derivative_indicator', symbols=sym, start_date=start_date, end_date=end_date,fields='PETTM, PB', df = 'True')
        if len(df_r) > 0:
            df_r = df_r.drop(['pub_date'], axis=1, inplace=False)
            df_r= df_r.fillna('NULL')
            for i in range(0, len(df_r)):
                data_string = '\'' + key + '\',\'' + df_r.end_date.iloc[i].strftime('%Y-%m-%d') + '\','  + str(round(df_r.PETTM.iloc[i],3)) + ','  + str(round(df_r.PB.iloc[i],3)) + ');'
                insert_sql =  'insert into data.stk_ratio values(' + data_string
                try:
                    fill_data(insert_sql)
                except Exception as e:
                    print(e)
                    print(insert_sql)
        print(sym + ' is updated')


def fill_ratio_data():
    items = 'symbol, date'
    endDate = (datetime.now().date() + timedelta(days=-1)).strftime('%Y%m%d')
    startDate = (datetime.now().date() + timedelta(days=-15)).strftime('%Y%m%d')
    table = 'idx_price'
    symbol_list = ['000001.SH']
    db_data = get_data(items, table, symbol_list, startDate, endDate)

    date_list = []
    for i in range(0, len(db_data)):
        date_list.append(db_data[i][1])

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
                fill_data(insert_sql)
            except Exception as e:
                print(e)

        print(symbol_list3 + 'is filled.')


update_stk_adj_factor()
update_stk_PEPB()
fill_ratio_data()