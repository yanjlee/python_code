# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from ConnectDB import connDB, connClose, get_all_data, get_data, fill_data
from datetime import timedelta, datetime
import tushare as ts
import urllib.request

df = ts.get_k_data('000001',index=True,start='2016-10-01', end='2016-10-31')



conn, cur = connDB()
items = 'symbol, max(date) as date'
tables = 'idx_price'
condition = ' where symbol not like \'%WI\' group by symbol order by symbol'
data_info = get_all_data(items, tables, condition)

idx_data = dict(data_info)
## http://hq.sinajs.cn/list=sz399005,sh000001
for j in idx_data:
    if j.startswith('0'):
        symbol_code = 'sh' + j[0:6]
    else:
        symbol_code = 'sz' + j[0:6]
    url = 'http://hq.sinajs.cn/list=' + symbol_code
    response_data = urllib.request.urlopen(url).read().decode('gb2312')
    i_data = response_data.split(',')
    chgrate = round((float(i_data[3]) - float(i_data[2])) * 100 / float(i_data[3]), 4)
    temp = [j, i_data[-3], i_data[1], i_data[4], i_data[5], i_data[3], chgrate, i_data[9]]
    insert_sql = 'insert into data.idx_price values(' + str(temp).replace('[', '').replace(']', '') + ');'
        # print(insert_sql)
    try:
        conn.cursor().execute(insert_sql)
    except Exception as e:
        print(e)
    print(j + ' is inserted. ')
    conn.commit()

## tushare
end_date = datetime.now().date().strftime('%Y-%m-%d')
for i in idx_data:
    start_date = (idx_data[i]+timedelta(1)).strftime('%Y-%m-%d')
    if start_date > end_date:
        continue
    idx_price = ts.get_h_data(i[0:6], index=True, start=start_date, end=end_date)



    # if len(w_data.Data) <= 1 or w_data.Data[0][1] == None:
    #     continue

    # for s in range(0, len(w_data.Times)):
    #     temp = []
    #     temp.append(i)
    #     temp.append(w_data.Times[s].strftime('%Y-%m-%d'))
    #     for r in range(0, len(w_data.Fields)):
    #         temp.append(w_data.Data[r][s])
    #     insert_sql = 'insert into data.idx_price values(' + str(temp).replace('[', '').replace(']', '') + ');'
        # print(insert_sql)
    #     try:
    #         conn.cursor().execute(insert_sql)
    #     except Exception as e:
    #         print(e)
    # print(i + ' is inserted. ')
    # conn.commit()
connClose(conn, cur)
