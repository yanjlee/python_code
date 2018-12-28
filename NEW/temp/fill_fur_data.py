# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from ConnectDB import connDB, connClose, get_data, get_all_data
from datetime import datetime as dt, timedelta
from WindPy import w

conn, cur = connDB()

# symbol = 'IC1806.CFE'
def fill_fur_price(symbol):
    ## 获取缺失的datetime列表
    req_sql = 'select std_time from (select datetime as std_time from data.fur_price where symbol =\'000300.SH\') a left join (select datetime as symbol_time FROM data.fur_price where symbol =\'' + symbol + '\') b on a.std_time =b.symbol_time where b.symbol_time is null and a.std_time > (SELECT min(datetime) FROM data.fur_price where symbol =\'' + symbol + '\')'
    try:
        cur.execute(req_sql)
        std_date = cur.fetchall()
    except Exception as e:
        print(e)
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

symbol_list = ['ZN1807.SHF','CU1807.SHF','SR809.CZC','AU1812.SHF','AL1807.SHF','AL1809.SHF','IC1801.CFE','IC1802.CFE','IC1803.CFE','IC1804.CFE','IC1805.CFE','IC1806.CFE','IC1809.CFE','IF1801.CFE','IF1802.CFE','IF1803.CFE','IF1804.CFE','IF1805.CFE','IF1806.CFE','IF1809.CFE','IH1801.CFE','IH1802.CFE','IH1803.CFE','IH1804.CFE','IH1805.CFE','IH1806.CFE','IH1809.CFE','OI809.CZC','T1806.CFE','T1809.CFE']
# symbol_list= ['IC1806.CFE ']
for j in symbol_list:
    for i in range(0,10):
        fill_fur_price(j)

connClose(conn, cur)