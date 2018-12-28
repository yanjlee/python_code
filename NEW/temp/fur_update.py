# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from ConnectDB import fill_data
import pandas as pd
from WindPy import w
from ConnectDB import connDB, connClose, get_all_data
from datetime import timedelta

conn, cur = connDB()

w.start()
# # fur_symbols = ['T1806.CFE,T1809.CFE,T1812.CFE,IF1806.CFE','IF1804.CFE','IF1805.CFE','IF1809.CFE','IH1804.CFE','IH1805.CFE','IH1806.CFE','IH1809.CFE','IC1804.CFE','IC1805.CFE','IC1806.CFE','IC1809.CFE']
#
def  update_fur(symbol):
    fur_data = w.wsi(symbol, "open,close,high,low", "2018-08-06 09:00:00", "2018-08-27 23:01:00", "periodstart=09:00:00;periodend=23:01:00")
    # fur_data = w.wsi(symbol, "open,close,high,low", "2018-07-20 09:30:00", "2018-07-20 15:00:00","periodstart=09:30:00;periodend=15:00:00")
    for i in range(len(fur_data.Times)):
        temp_price = []
        for j in range(len(fur_data.Fields)):
            temp_price.append(fur_data.Data[j][i])
        temp_price = str(temp_price).replace('[','').replace(']','')
        insert_sql = 'insert into data.fur_price values(\'' + fur_data.Codes[0] + '\',\'' + str(fur_data.Times[i]) + '\',' + temp_price + ');'
        fill_data(insert_sql)
    print(fur_data.Codes[0] + ' is inserted')

def calc_ema(j):
    items = 'datetime, close'
    table = 'fur_price'
    condition = ' where symbol = \'' + j + '\' order by datetime desc limit 240'
    idx_data = get_all_data(items, table, condition)
    idx_price = dict(idx_data)
    df_price = pd.DataFrame(list(idx_price.values()), columns=['close'], index=idx_price.keys())
    df_price.sort_index(inplace=True)

    ma_list = [5, 21, 55]
    for ma in ma_list:
        df_price['ema' + str(ma)] = df_price['close'].ewm(span=ma, min_periods=0, adjust=True,
                                                          ignore_na=False).mean()
    df_price = df_price.drop(columns=['close'])
    for h in range(0, len(df_price)):
        insert_sql = 'insert into data.fur_price_tec values(\'' + j + '\',\'' + df_price.index[h].strftime(
            '%Y-%m-%d %H:%M:%S') + '\', ' + str(list(df_price.iloc[h])).replace('[', '').replace(']','') + ');'
        fill_data(insert_sql)

def fill_fur_price(symbol):
    ## 获取缺失的datetime列表
    req_sql = 'select std_time from (select datetime as std_time from data.fur_price where symbol =\'000300.SH\') a left join (select datetime as symbol_time FROM data.fur_price where symbol =\'' + symbol + '\') b on a.std_time =b.symbol_time where b.symbol_time is null and a.std_time > (SELECT min(datetime) FROM data.fur_price where symbol =\'' + symbol + '\')'
    try:
        cur.execute(req_sql)
        std_date = cur.fetchall()
    except Exception as e:
        print(e)

    if len(std_date) > 0 :
        std_time = []
        for i in range(0, len(std_date)):
            std_time.append((std_date[i][0] - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'))

        ## 获取前一分钟收盘价，准备注入
        close_sql = 'select datetime, close from data.fur_price where datetime in (' + str(std_time).replace('[','').replace(']','') + ') and symbol = \'' + symbol + '\''
        try:
            cur.execute(close_sql)
            fur_data = cur.fetchall()
        except Exception as e:
            print(e)

        fur_price = []
        for j in range(0, len(fur_data)):
            temp = []
            temp.append((fur_data[j][0] + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'))
            temp.append(float(fur_data[j][1]))
            temp.append(float(fur_data[j][1]))
            temp.append(float(fur_data[j][1]))
            temp.append(float(fur_data[j][1]))
            fur_price.append(temp)

        ## 插入丢失行数据
        for k in fur_price:
            insert_sql = 'insert into data.fur_price values( \'' + symbol + '\',' + str(k).replace('[','').replace(']','') + ');'
            # print(insert_sql)
            try:
                cur.execute(insert_sql)
            except Exception as e:
                print(e)
        conn.commit()
        print(symbol + ' is filled.')

# symbol_list = ['ZN1807.SHF','CU1807.SHF','SR809.CZC','AU1812.SHF','AL1807.SHF','AL1809.SHF','IC1801.CFE','IC1802.CFE','IC1803.CFE','IC1804.CFE','IC1805.CFE','IC1806.CFE','IC1809.CFE','IF1801.CFE','IF1802.CFE','IF1803.CFE','IF1804.CFE','IF1805.CFE','IF1806.CFE','IF1809.CFE','IH1801.CFE','IH1802.CFE','IH1803.CFE','IH1804.CFE','IH1805.CFE','IH1806.CFE','IH1809.CFE','OI809.CZC','T1806.CFE','T1809.CFE']
# symbol_list=['ZN1807.SHF','CU1807.SHF','SR809.CZC','AU1812.SHF','AL1807.SHF','AL1809.SHF','RB1810.SHF','OI809.CZC']
symbol_list=['RB1901.SHF']
# symbol_list=['000016.SH','000300.SH','000905.SH']

for i in symbol_list:
    update_fur(i)
    # calc_ema(i)

# for k in symbol_list:
#     for g in range(0, 10):
#         fill_fur_price(k)


connClose(conn, cur)
# #
# #
# # items = 'symbol'
# # table = 'fur_price'
# # condition = ' group by symbol order by symbol'
# # idx_data = get_all_data(items, table, condition)
# # symbols = []
# symbols = ['T1806.CFE','T1809.CFE','T1812.CFE']
# # for i in idx_data;;
# #     symbols.append(i[0])
#
# for j in symbols:
#     calc_ema(j)

# items = 'symbol'
# table = 'b_list'
# condition = 'order by symbol'
# symbol_data = get_all_data(items, table, condition)
# b_list = []
# for i in symbol_data:
#     b_list.append(i[0])

# print('hello {first} and {second}'.format(first='df', second='another df'));
# import QuantLib as ql
#
# date = ql.Date(7, 5, 2017)#定义了2017年5月7号这样的一个date
# print (date)
# print(date.dayOfMonth())#获取这个date是该月的第几天
# print (date.dayOfYear())#获取这个date是本年的第几天
# print (date.weekday())
