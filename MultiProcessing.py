# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from ConnectDB import connDB, connClose, get_data, get_all_data, fill_data
import pandas as pd
from multiprocessing import Pool


def calc_ema(j):
    items = 'date, close'
    table = 'stk_price_backward'
    condition = ' where symbol = \'' + j + '\' order by date asc'
    idx_data = get_all_data(items, table, condition)
    idx_price = dict(idx_data)
    df_price = pd.DataFrame(list(idx_price.values()), columns=['close'], index=idx_price.keys())

    ma_list = [5, 10, 21, 40, 60]
    for ma in ma_list:
        df_price['ema' + str(ma)] = df_price['close'].ewm(span=ma, min_periods=0, adjust=True, ignore_na=False).mean()
    df_price = df_price.drop(columns=['close'])
    for h in range(0, len(df_price)):
        insert_sql = 'insert into data.stk_price_tec values(\'' + j + '\',\'' + df_price.index[h].strftime('%Y-%m-%d') + '\', ' + str(list(df_price.iloc[h])).replace('[','').replace(']',');')
        fill_data(insert_sql)

    print(j + ' is inserted')



if __name__ == '__main__':
    items = 'symbol'
    table = 'stk_price_backward'
    condition = ' group by symbol order by symbol'
    idx_data = get_all_data(items, table, condition)
    symbols = []
    for i in idx_data:
        symbols.append(i[0])

    pool = Pool(processes=4)
    pool.map(calc_ema, symbols)
    pool.close()
    pool.join()