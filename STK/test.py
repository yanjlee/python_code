# coding=UTF-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import pandas as pd
from ConnectDB import get_all_data,fill_data
import arrow
import numpy as np
from math import log as lg, exp
from datetime import timedelta, datetime
import talib as ta
from STK.tsdata import get_k_stk as get_k

# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')
start = '2019-01-01'
end='2019-01-04'

i = '000002.SZ'
if i.startswith('6'):
    symbol = 'SHSE.' + i.replace('.SH', '')
else:
    symbol = 'SZSE.' + i.replace('.SZ', '')

gm_data = get_history_instruments(symbols=[symbol],fields='symbol,trade_date,adj_factor',start_date= start,end_date=end,df=True)
# if len(gm_data)  == 0:
#     continue
for i in range(0,len(gm_data)):
    insert_gm = 'insert into data.stk_adj_factor values(\'' + symbol + '\',\'' + gm_data['trade_date'][i].strftime('%Y-%m-%d') + '\',' + str(round(gm_data['adj_factor'][i], 6)) + ');'
    print(insert_gm)

# start = '2019-01-01'
# end='2019-01-04'
# data = get_history_instruments(symbols=['SHSE.601318'],fields='symbol,trade_date,adj_factor',start_date= start,end_date=end,df=True)
# print(data)
# def get_all_gm(symbol, s_time):
#     df = pd.DataFrame()
#     n = int((dt.now() - dt.strptime(s_time, '%Y-%m-%d')).days/365.24) + 1
#     for i in range(0, n):
#         start_date = (dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * i).strftime('%Y-%m-%d')
#         end_date = max(dt.now().date().strftime('%Y-%m-%d'), (dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * (i+1)).strftime('%Y-%m-%d'))
#         df_dy = get_fundamentals(table='trading_derivative_indicator', symbols=symbol, start_date=start_date,end_date=end_date, fields='DY', df='True')
#         df = pd.concat([df,df_dy], axis=0)
#         df = df.drop_duplicates()
#     return(df)
#
#
# def update_div_yield(symbol_list, start_date, end_date):
#     for symbol in symbol_list:
#         if symbol.startswith('6'):
#             sym = 'SHSE.' + symbol.replace('.SH', '')
#         else:
#             sym = 'SZSE.' + symbol.replace('.SZ', '')
#
#         items = 'rpt_date as date'
#         table = 'stk_fina_calc'
#         condition = ' where symbol = \'' + symbol + '\' and rpt_date between \'' + start_date + '\' and \'' + end_date + '\' and rpt_date is not null order by date asc'
#         r_data = get_all_data(items, table, condition)
#         rpt_date = pd.DataFrame(list(r_data), columns=['rpt'])
#
#         dy_data = get_all_gm(sym,start_date)
#         if len(dy_data) == 0 or 'DY' not in list(dy_data.columns):
#             continue
#         dy_data.drop(['end_date', 'symbol'], axis=1, inplace=True)
#         df = dy_data.set_index('pub_date')
#         begin_date = start_date
#         dy = 'NULL'
#         dy_list = []
#         dy_data.to_csv('test1.csv')
#         for i in range(0, len(rpt_date)):
#             df_dy = df[begin_date:rpt_date.rpt[i]]
#             for j in range(0, len(df_dy)):
#                 if pd.isna(df_dy.DY[j]):
#                     # dy = 'NULL'
#                     continue
#                 else:
#                     dy = round(df_dy.DY[j], 3)
#             dy_list.append([rpt_date.rpt[i], dy])
#             begin_date = rpt_date.rpt[i]
#
#         print(dy_list)
#         for k in dy_list:
#             update_dy = 'UPDATE data.stk_fina_calc SET div_yield = ' + str(k[1]) + ' where symbol = \'' + symbol + '\' and rpt_date = \'' + k[0].strftime('%Y-%m-%d') + '\';'
#             print(update_dy)
#             # try:
#             #     fill_data(update_dy)
#             # except Exception as e:
#             #     print(e)
#             #     print(update_dy)
#         print(symbol + ': div_yield is updated.')
#
# quartly_date = ['2018-09-30','2018-06-30','2018-03-31','2017-12-31','2017-09-30','2017-06-30','2017-03-31','2016-12-31','2016-09-30','2016-06-30','2016-03-31','2015-12-31','2015-09-30','2015-06-30','2015-03-31','2014-12-31','2014-09-30','2014-06-30','2014-03-31','2013-12-31','2013-09-30','2013-06-30','2013-03-31','2012-12-31','2012-09-30','2012-06-30','2012-03-31','2011-12-31','2011-09-30','2011-06-30','2011-03-31','2010-12-31','2010-09-30','2010-06-30','2010-03-31','2009-12-31']
# start_date = quartly_date[-1]
# end_date = quartly_date[0]
# symbol_list = ['000333.SZ']#,'000022.SZ']
# # df = get_df(quartly_date)
# # update_eps_roe(symbol_list, df)
# # update_roic(symbol_list, df,start_date, end_date)
# update_div_yield(symbol_list, start_date, dt.now().date().strftime('%Y-%m-%d'))
# requestDate = '2018-12-24'
# MKT_CAP = 5000000000
# PE =30
# DIVIDEND_RATE = 1.5
#
# items = 'symbol'
# table = 'stk_price'
# condition = 'where mktcap > ' + str(MKT_CAP) + ' and date =\'' + requestDate +'\' order by symbol'
# mkt_data = get_all_data(items, table, condition)
# divSet1 = str(mkt_data).replace(',), (',',').replace('((','(').replace(',))',')')
# print(divSet1)
#
# # 4. PE值过滤
# items = 'symbol'
# table = 'stk_ratio'
# condition = 'where symbol in ' + divSet1 + ' and pe_ttm > 0 and pe_ttm <= ' + str(PE) + ' and date = \'' + requestDate + '\' order by symbol'
# pe_data = get_all_data(items, table, condition)
# divSet2 =  str(pe_data).replace(',), (',',').replace('((','(').replace(',))',')')
# print(divSet2)
#
# # 5. 股息收益率要大于5年国债收益率
# items = 'a.symbol'
# table = 'stk_fina_calc'
# condition = ' a inner join (SELECT symbol, max(date) as date FROM data.stk_fina_calc where rpt_date <= \'' + requestDate + '\' and symbol in ' + divSet2 + ' group by symbol) b on a.symbol =b.symbol and a.date = b.date where a.div_yield > ' + str(DIVIDEND_RATE) + 'order by a.symbol'
# div_yield_data = get_all_data(items, table, condition)
# divSet3 = str(div_yield_data).replace(',), (',',').replace('((','(').replace(',))',')')
# print(divSet3)


# items = 'symbol, max(date)'
# table = 'stk_fina_calc'
# condition = ' where symbol in ' + divSet3 + ' and rpt_date < \'' + requestDate + '\' group by symbol order by symbol'
# quarter_data = get_all_data(items, table, condition)
# divSet4= dict(quarter_data)
#
# ROE = 15
#
# set_roe_value_avg = []
# set_roe_remove = []
# set_roe = {}
# for k, v in divSet4.items():
#     end = v.strftime('%Y-%m-%d')
#     start = arrow.get(v).replace(years=-3).date().strftime('%Y-%m-%d')
#     items = 'roe_ttm'
#     table = 'stk_fina_calc'
#     condition = ' where symbol = \'' + k + '\'  and date between \'' + start + '\' and \'' + end + '\' and roe_ttm is not null order by date asc'
#     roe_data = get_all_data(items, table, condition)
#     if len(roe_data) < 7:
#         set_roe_remove.append(k)
#         continue
#
#     e_avg_temp = 1  # 计算3年ROE指数平均值
#     for roe_q in roe_data:
#         e_avg_temp = e_avg_temp * (1 + roe_q[0] / 100)
#         if roe_q[0] < ROE: ## 任何一期低于标准，淘汰
#             set_roe_remove.append(k)
#     if e_avg_temp <= 1:  # 3年ROE指数平均值低于1直接淘汰
#         set_roe_remove.append(k)
#         continue
#     set_roe_value_avg.append(100 * (float(e_avg_temp) ** (1 / len(roe_data)) - 1))
#     set_roe[k] = set_roe_value_avg[-1]
#
#     if set_roe_value_avg[-1] <= ROE or roe_data[-1][-1] <= ROE:  # 3年ROE指数均值或最后一期ROE低于低于标准者剔除
#         set_roe_remove.append(k)
#         del set_roe[k]
# divSet5 = list(set(list(divSet4.keys())).difference(set(set_roe_remove)))
#
# roe_std = {}
# roe_to_pb = {} # 经济学意义： 100* NI / MarketValue， 值越高越好，低值表明赚钱能力过低，MV可以约等于Asset
# roe_std_to_pb = {}
# std_to_roe = {}
# set_std_remove = []
# for k in divSet5:
#     end2 = divSet4[k].strftime('%Y-%m-%d')
#     start2 = arrow.get(divSet4[k]).replace(years=-3).date().strftime('%Y-%m-%d')
#     items = 'roe_ttm'
#     table = 'stk_fina_calc'
#     condition = ' where symbol = \'' + k + '\'  and date between \'' + start2 + '\' and \'' + end2 + '\' and roe_ttm is not null order by date asc'
#     roe_data = get_all_data(items, table, condition)
#     roe_ttm_list = []
#     for j in roe_data:
#         roe_ttm_list.append(float(j[0]))
#     roe_std[k] = float(np.std(roe_ttm_list))
#
#     item2 = 'pb'
#     table2 = 'stk_ratio'
#     condition2 = ' where symbol = \'' + k + '\' order by date desc limit 1'
#     pb_data = get_all_data(item2, table2, condition2)
#     pb_v = float(pb_data[0][0])
#     if len(pb_data) == 0 or pb_v < 1 or pb_v > 50 or set_roe[k] / pb_v < 4:  ##  PB需要大于1，否则RI(留存收益）为负
#         set_std_remove.append(k)
#         roe_std.pop(k)
#         continue
#     elif roe_std[k] / pb_v > 3:
#         set_std_remove.append(k)
#         roe_std.pop(k)
#         set_roe.pop(k)
#         continue
#     else:
#         roe_std_to_pb[k] = roe_std[k] / pb_v
#         roe_to_pb[k] = set_roe[k] / pb_v
#         std_to_roe[k] = roe_std[k] / set_roe[k]
#
# divSet6 = list(set(divSet5).difference(set(set_std_remove)))
#
# ## Sort them, ln 自然对数计算
# roe_std_to_pb = dict(sorted(roe_std_to_pb.items(), key=lambda x: x[1], reverse=False)) # 一定范围
# roe_to_pb = dict(sorted(roe_to_pb.items(), key=lambda x: x[1], reverse=False)) # 越大越好
# set_roe = {k: v for k, v in set_roe.items() if k in divSet6}
# set_roe = dict(sorted(set_roe.items(), key=lambda x: x[1], reverse=True)) # 越大越好
# std_to_roe = dict(sorted(std_to_roe.items(), key=lambda x: x[1], reverse=False)) # 越小越好
#
# roe_to_pb_ln = {}
# roe_ln ={}
# roe_std_to_pb_ln = {}
# std_to_roe_ln = {}
#
# min_roe2pb = sorted(roe_to_pb.values())[0]
# min_roe = sorted(set_roe.values())[0]
# max_std2roe =  sorted(std_to_roe.values())[-1]
# max_std2pb = sorted(roe_std_to_pb.values())[-1]
#
# for k in divSet6:
#     roe_to_pb_ln[k] = exp(min_roe2pb/roe_to_pb[k])
#     roe_ln[k] = exp(min_roe/set_roe[k])
#     roe_std_to_pb_ln[k] = exp(roe_std_to_pb[k]/max_std2pb)
#     std_to_roe_ln[k] = exp(std_to_roe[k]/max_std2roe)

