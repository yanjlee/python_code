# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import logging as log
import numpy as np
from ConnectDB import connDB, connClose, get_all_data
from CIGRG.WindPy import w

# file1 = 'D:/temp1/wind.txt' #Stock 下载、处理和导入数据路径
# file2 = 'D:/temp1/wind1.txt'
# file3 = 'D:/temp1/wind2.txt'
log.basicConfig(
    level=log.DEBUG,
    format="%(levelname)s: %(message)s")

# code_list = []
# date_list = []
# standard_list = []

items = 'symbol, ipo'
table = 'stk_info'
condition = ' order by symbol'
ipo_date = get_all_data(items, table, condition)
stk_ipo = {}
stk_list = []
for i in ipo_date:
    stk_ipo[i[0]] = i[1]
    stk_list.append(i[0])

w.start()
conn, cur = connDB()
# pb
for i in range(1044, len(stk_list)):
    start_date = stk_ipo[stk_list[i]].strftime('%Y-%m-%d')
    if start_date < '2010-01-01':
        start_date = '2010-01-01'

    wind_data = w.wsd(stk_list[i], "pb_lf", start_date, "2018-03-18",  "")
    for k in range(0, len(wind_data.Times)):
        if np.isnan(wind_data.Data[0][k]):
            continue
        update_sql = 'update data.stk_ratio set pb = \'' + str(wind_data.Data[0][k]) + '\' where symbol =\'' + wind_data.Codes[0] + '\' and date = \'' + wind_data.Times[k].strftime('%Y-%m-%d') + '\''

        try:
            cur.execute(update_sql)

        except Exception as e:
            print(e)
            print(update_sql)
    conn.commit()
    print(str(stk_list[i]) + ' is updated into DB')

connClose(conn, cur)


# with open(file3, 'r') as file_line:
#     content = file_line.readlines()
#     code_list = content[0].replace('[', '').replace(']', '').replace(' ', '').replace('\'', '').strip().split(',')
#     standard_date = content[1].replace('),','|').replace('datetime.date(','').replace(' ','').replace(',','-').replace('[', '').replace(']', '').replace(')','').strip().split('|')
#     temp = list(content[2].replace(']]','').replace('[[','').strip().split('], ['))
#     data_list = []
#     for j in temp:
#         j = j.replace(' ','').split(',')
#         data_list.append(j)
#
#     conn, cur = connDB()
#     for m in range(0, len(code_list)):
#         for n in range(0, len(standard_date)):
#             if standard_date[n] < stk_ipo[code_list[m]].strftime('%Y-%m-%d') or data_list[m][n] == 'nan'  or data_list[m][n] == 'None':
#                 continue
#             update_sql = 'update data.stk_fina_calc set div_yield = \'' +  data_list[m][n] + '\' where symbol = \'' + code_list[m] + '\' and date = \'' + standard_date[n] + '\''
#             # print(update_sql)
#             try:
#                 cur.execute(update_sql)
#             except Exception as e:
#                 print(e)
#                 print(update_sql)
#     connClose(conn, cur)


# file_line2 = with open(file2, 'r') as
# file_line3 = open(file3, 'r')

# for i in file_line:
#     i = i.strip().split('|')
#     date_list.append(list(i))
#
# for j in file_line2:
#     code_list.append(j.strip())
#
# for k in file_line3:
#     standard_list.append(k.strip())
#
# file_line.close()
# file_line2.close()
# file_line3.close()


# items = 'symbol, ipo'
# table = 'stk_info'
# condition = ' order by symbol'
# ipo_date = get_all_data(items, table, condition)
# stk_ipo = {}
# stk_list = []
# for i in ipo_date:
#     stk_ipo[i[0]] = i[1]
#     stk_list.append(i[0])

# w.start()
# conn, cur = connDB()
# # pe_ttm
# for i in range(3437, len(stk_list)):
#     start_date = stk_ipo[stk_list[i]].strftime('%Y-%m-%d')
#     if start_date < '2010-01-01':
#         start_date = '2010-01-01'
#     try:
#         wind_data = w.wsd(stk_list[i], "pe_ttm", start_date, "2018-03-18",  "")
#         for k in range(0, len(wind_data.Times)):
#             if np.isnan(wind_data.Data[0][k]):
#                 continue
#             insert_sql = 'insert into data.stk_ratio (symbol, date, pe_ttm) values(\'' + wind_data.Codes[0] + '\',\'' + wind_data.Times[k].strftime('%Y-%m-%d') + '\',\'' + str(wind_data.Data[0][k]) + '\')'
#
#             try:
#                 cur.execute(insert_sql)
#                 conn.commit()
#             except Exception as e:
#                 print(e)
#
#         print(stk_list[i] + ' is loaded into DB')
#     except Exception as e:
#         print(e)
#         print('Get data failed on: ' + str(i) + ' - ' + stk_list[i])
# connClose(conn, cur)


# conn, cur = connDB()
# for m in range(0, len(code_list)):
#     for n in range(0, len(standard_list)):
#         if standard_list[n] < stk_ipo[code_list[m]].strftime('%Y-%m-%d'):
#             continue
#         insert_sql = 'insert into data.stk_fina_calc (symbol, date, rpt_date) values' '(\'' + code_list[m] + '\',\'' + standard_list[n] + '\',\'' + date_list[m][n] + '\')'
#         insert_sql = insert_sql.replace('\'None\'', 'default')
#         try:
#             cur.execute(insert_sql)
#         except Exception as e:
#             print(e)
# connClose(conn, cur)