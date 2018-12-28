# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import logging as log
import datetime
import tushare as ts
from datetime import timedelta, datetime
import pandas as pd
from ConnectDB import connDB, connClose, get_all_data,  fill_data


conn, cur = connDB()

def update_adj_price(symbol):

    items = 'ipo'
    table = 'stk_info'
    condition = ' where symbol=\'' + symbol + '\' '
    stk_data = get_all_data(items, table, condition)
    startDate = stk_data[0][0].strftime('%Y%m%d')
    endDate = (datetime.now().date() + timedelta(days=-1)).strftime('%Y%m%d')
    # startDate = (datetime.now().date() + timedelta(days=-5)).strftime('%Y%m%d')

    idx_item = 'date'
    idx_table = 'idx_price'
    idx_condition = ' where symbol = \'000001.SH\' and date between \'' + startDate + '\' and \'' + endDate +'\''
    db_data = get_all_data(idx_item, idx_table, idx_condition)

    date_list = []
    for i in range(0, len(db_data)):
        date_list.append(db_data[i][0])

    del_sql = 'delete from data.stk_price_forward where symbol = \'' + symbol + '\''
    try:
        cur.execute(del_sql)
    except Exception as e:
        print(e)
    conn.commit()


    try:
        pricedata = ts.get_k_data(symbol.replace('.SH','').replace('.SZ',''), ktype='D', autype='qfq', start=startDate, end=endDate);
        del pricedata['volume']
    except Exception as e:
        print(e)

    for h in range(0, len(pricedata)):
        if symbol.startswith('6'):
            values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SH\'')
        else:
            values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SZ\'')
        insql = 'insert into data.stk_price_forward  (date,open,close,high,low,symbol) values (' + values + ');'
        # print(insql)
        try:
            conn.cursor().execute(insql)
        except Exception as e:
            print(e)

    conn.commit()
    log.info(symbol + ' is inserted' )

    items2 = 'symbol, min(date), max(date)'
    table2 = 'stk_price_forward'
    condition = ' where date >= \'' + startDate + '\' and date <=\'' + endDate + '\' and symbol = \'' + symbol + '\''
    db_data2 = get_all_data(items2, table2, condition)
    for a in range(0, len(db_data2)):
        index_start = date_list.index(db_data2[a][1])
        index_end = date_list.index(db_data2[a][2])
        if index_start >= index_end:
            continue
    date_list_idx = date_list[index_start:]

    item3 = 'date, close'
    table3 = 'stk_price_forward'
    startDate3 = db_data2[a][1].strftime('%Y-%m-%d')
    endDate3 = db_data2[a][2].strftime('%Y-%m-%d')
    condition = ' where date >= \'' + startDate3 + '\' and date <=\'' + endDate3 + '\' and symbol = \'' + symbol + '\''
    stk_data = get_all_data(item3, table3, condition)
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
        insert_sql = 'insert into data.' + table3 + ' values (\'' + symbol + '\',\'' + str(e) + '\',\'' + str(
            float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\',\'' + str(
            float(fill_stk[e])) + '\',\'' + str(float(fill_stk[e])) + '\');'

        try:
            cur.execute(insert_sql)
            print(insert_sql)
        except Exception as e:
            print(e)
    conn.commit()
    print(symbol + ' is filled.')





def update_stk_price_tec(j):

    def calc_ema(j):
        items = 'date, close'
        table = 'stk_price_forward'
        condition = ' where symbol = \'' + j + '\' order by date desc'
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
        condition = ' where symbol=\'' + j + '\'  order by date desc'
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
        for h in range(0, len(df)):
            insert_sql = 'update data.stk_price_tec set atr13 =\'' + str(df['atr13'].iloc[h]) + '\' , atr21 = \'' + str(
                df['atr21'].iloc[h]) + '\' where symbol =\'' + j + '\' and date = \'' + df.index[h] + '\';'
            fill_data(insert_sql)
        print(j + '\'s ATR data are updated.')

    del_sql = 'delete from data.stk_price_tec where symbol = \'' + j + '\''
    try:
        cur.execute(del_sql)
    except Exception as e:
        print(e)
    conn.commit()
    calc_ema(j)
    calc_atr(j)


update_adj_price('601318.SH')
update_stk_price_tec('601318.SH ')

connClose(conn, cur)