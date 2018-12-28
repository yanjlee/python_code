# -*- coding: utf-8 -*-
"""
@author: GuoJun
"""

from CIGRG.WindPy import w
import logging as log

# a = ts.get_industry_classified()
#
# b = ts.get_concept_classified()



# BASE_DIR = os.path.dirname(__file__)
# LOG_PATH = BASE_DIR + '/'
# LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))) + '.log'
log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level = log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format = "%(levelname)s: %(message)s")

# #############################
# # 常量设置
# PE = 30
# PB = 3
# ROE = 6
# DIVIDEND_RATE = 0.038
# WEIGHT = 0.618
# MKT_CAP = 5000000000
# TOP_STOCK_NUMBER = 10
#
# requestDate = '2012-06-06'
#############################
# import re
#
# def checkio(data):
#     if len(data) < 10:
#         return False
#     elif re.match("[a-zA-Z0-9]+", data)：
#     #replace this for solution
#         return True
#
#
# if __name__ == '__main__':
#     #These "asserts" using only for self-checking and not necessary for auto-testing
#     assert checkio('A1213pokl') == False, "1st example"
#     assert checkio('bAse730onE4') == True, "2nd example"
#     assert checkio('asasasasasasasaas') == False, "3rd example"
#     assert checkio('QWERTYqwerty') == False, "4th example"
#     assert checkio('123456123456') == False, "5th example"
#     assert checkio('QwErTy911poqqqq') == True, "6th example"
#     print("Coding complete? Click 'Check' to review your tests and earn cool rewards!")

# a = ['000651.SZ', '600000.SH', '600028.SH', '600104.SH', '600548.SH', '600660.SH', '600999.SH', '601006.SH',
#      '601566.SH', '601988.SH','kkk']
# b = ['000651.SZ', '601988.SH','600000.SH', '600028.SH', '600104.SH', '600548.SH', '600660.SH', '600999.SH', '601006.SH',
#      '601566.SH','test' ]
# d = []
# e = ['600028.SH', '601566.SH']
# # if a != b:
# #     sell_list = set(a).difference(set(b))
# #     buy_list = set(b).difference(set(a))
#     f = {'a':{'aa':12, 'bb':14},'b':{'cc':15, 'dd':16}}
# x = np.arange(0, 8, 1)
# cumulative_return = 300.24
# annualized_return = 31.21
# sharp_ratio = 1.067
# max_draw_down = -30.11
# cumulative_return_list = [1, 2, 3, 4, 5, 6, 7, 8]
# hs300_cumulative = [1.2, 2.5, 3.1, 4.5, 5.5, 6.4, 7.4, 8.8]
# pic_txt = '总收益：' + str(cumulative_return) + '% 年化收益：' + str(annualized_return) + '%' + '\n' + '夏普率:' + str(
#     sharp_ratio) + ' 最大回撤：' + str(max_draw_down) + '%'
# log.info(pic_txt)
# y1 = np.array(cumulative_return_list)
# y2 = np.array(hs300_cumulative)
#
# plt.plot(x, y1, 'r', label='Portfolio')
# plt.plot(x, y2, 'b', label='HS300')
# plt.grid(True)
# plt.axis('tight')
# plt.xlabel('Date')
# plt.ylabel('Return')
# plt.legend(loc='upper left', frameon=False)
# # plt.xticks(x, rotation=30)
# font = {'family': 'SimHei', 'color': 'black', 'weight': 'normal', 'size': 11,}
# plt.text(0, 6.5, pic_txt, fontdict=font)
# # plt.show()


# code,代码
# name,名称
# industry,所属行业
# area,地区
# pe,市盈率
# outstanding,流通股本(亿)
# totals,总股本(亿)
# totalAssets,总资产(万)
# liquidAssets,流动资产
# fixedAssets,固定资产
# reserved,公积金
# reservedPerShare,每股公积金
# esp,每股收益
# bvps,每股净资
# pb,市净率
# timeToMarket,上市日期
# undp,未分利润
# perundp, 每股未分配
# rev,收入同比(%)
# profit,利润同比(%)
# gpr,毛利率(%)
# npr,净利润率(%)
# holders,股东人数

# df = ts.get_stock_basics()
# # df1 = df[(df['timeToMarket'] < int((datetime.now() - timedelta(365 * 3)).strftime('%Y%m%d'))) & (df['pe'] <= 30) & (
# #         df['pe'] > 0) & (df['gpr'] > 10) & (df['npr'] > 6) & (df['pb'] > 0) & (df['pb'] < 8) & (df['esp'] > 0) & (
# #                  df['bvps'] > 0) & (df['reservedPerShare'] > 0)]
# df = df[(df['timeToMarket'] < int((datetime.now() - timedelta(365 * 3)).strftime('%Y%m%d')))]
# df = df[(df['area'] != '黑龙江') & (df['area'] != '吉林') & (df['area'] != '辽宁')]
# requestDate = '2015-01-16'
# MKT_CAP = 5000000000
#
# divSet = []
# # IPO日期过滤掉上市时间低于3年的公司
# # setValue_ipo = w.wsd(divSet, "ipo_date", requestDate, requestDate, "TradingCalendar=SZSE")
# set_ipo_remove = []
# for a in range(0, len(ipo_data)):
#     divSet.append(ipo_data[a][0])
#     if ipo_data[a][1] >= datetime.date(datetime.strptime(requestDate, '%Y-%m-%d') - relativedelta(years=3)):
#         set_ipo_remove.append(ipo_data[a][0])
# divSet = list(set(divSet).difference(set(set_ipo_remove)))
#
# # 过滤掉总市值低于特定值公司，排除小市值公司策略的干扰
# items = 'symbol, mktcap'
# table = 'his_price_stk'
# condition = ' where date = \'' + requestDate + '\' and symbol in (' + str(divSet).replace('[', '').replace(']',
#                                                                                                            '') + ') order by symbol'
# mkt_data = get_all_data(items, table, condition)
# set_marketCap_remove = []

# setValue_marketCap = w.wsd(divSet, "mkt_cap_ashare2", requestDate, requestDate,"unit=1;currencyType=;TradingCalendar=SZSE")
# for b in range(0, len(mkt_data)):
#     if mkt_data[b][1] <= MKT_CAP:
#         set_marketCap_remove.append(mkt_data[b][0])
# divSet = list(set(divSet).difference(set(set_marketCap_remove)))

# ds =  ts.get_index()
# DF.drop(‘column_name’,axis=1, inplace=True)
# aqicsv[['x','y']][(aqicsv.FID >10000) | (aqicsv.predictaqi_norm1 >150)]

# startDate = '2012-01-01'
# endDate = '2015-12-31'
# data  =  ts.get_k_data('002456', ktype='D', autype='qfq', start=startDate, end=endDate);

# data = ts.get_growth_data(2014,3)

# # di = ts.get_hist_data('950102')
# def get_hs300():# 获取沪深300交易日期和涨跌幅作为基准参考
#     conn, cur = connDB()
#     query_sql = 'select date, close from data.his_price_idx where symbol = \'399300.SZ\' and date between \'' + startDate + '\' and \'' + endDate + '\' order by date'
#     try:
#         cur.execute(query_sql)
#         hs300_data = cur.fetchall()
#     except Exception as e:
#         print(e)
#
#     trade_date = []
#     hs300_close = []
#     for g in range(0, len(hs300_data)):
#         trade_date.append(hs300_data[g][0])
#         hs300_close.append(hs300_data[g][1])
#
#     connClose(conn, cur)
#     return(trade_date, hs300_close)
#
# def test_p():
#     log.info(trade_date)
#     log.info(hs300_close)
#
# trade_date, hs300_close = get_hs300()
# test_p()

# trade_date = HS300.Times
# dateinfo = exeQuery(cur,
#                     'select symbol,maxdate FROM data.id_list where source = \'' + table + '\'order by symbol').fetchall()
# maxdate = dict(dateinfo)
# symbolList = tuple(maxdate)
# symbolList = sorted(symbolList)
# enddate = time.strftime('%Y%m%d', time.localtime(time.time()))

# connClose(conn, cur)

# spread_weight = np.around(np.linspace(0.10, 0.20, 11), 2)
# stock_weight = np.around(np.linspace(0.10, 0.40, 21), 2)
# base_weight = np.around(np.linspace(0.10, 0.40, 21), 2)
# diff_weight = np.around(np.linspace(0.10, 0.40, 21), 2)
# rbp_weight = np.around(np.linspace(0.10, 0.40, 21), 2)
# rbs_weight = np.around(np.linspace(0.10, 0.40, 21), 2)
#
# # fac_weight=[[spr_weight,sto_weight,b_weight,d_weight,rp_weight,rs_weight] for spr_weight in spread_weight for sto_weight in stock_weight for b_weight in base_weight for d_weight in diff_weight  for rp_weight in rbp_weight for rs_weight in rbs_weight if spr_weight+sto_weight+b_weight+d_weight+rp_weight+rs_weight==1]
# # fac_weight=DataFrame(fac_weight,columns=['spread_weight','stock_weight','base_weight','diff_weight','rbp_weight','rbs_weight']).T
#
# fac_weight_0 = [(spread_wei, stock_wei, base_wei, diff_wei, rbp_wei, rbs_wei) for spread_wei in spread_weight for
#               stock_wei in stock_weight for base_wei in base_weight for diff_wei in diff_weight for rbp_wei in
#               rbp_weight for rbs_wei in rbs_weight if
#                 (spread_wei + stock_wei + base_wei + diff_wei + rbp_wei + rbs_wei) == 1]
# fac_weight = DataFrame(fac_weight_0, columns=['spread_weight', 'stock_weight', 'base_weight', 'diff_weight', 'rbp_weight',
#                       'rbs_weight']).T

# divSet = ['002456.SZ','600036.SH','000001.SZ']
# DIVIDEND_RATE = 0.01
# requestDate = '2018-03-16'
# ROE = 12
# PE = 30
#
# items = 'symbol, ipo'
# table = 'stk_info'
# condition = ' order by symbol'
# ipo_date = get_all_data(items, table, condition)
# stk_ipo = {}
# stk_list = []
# for i in ipo_date:
#     stk_ipo[i[0]] = i[1]
#     stk_list.append(i[0])
#
#
# requestDate = '2012-04-09'
#
# date_temp = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-1).ceil("quarter").date()
# date_temp2 = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-2).ceil("quarter").date()
# date_temp3 = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-3).ceil("quarter").date()
# rpt_date = date.strftime(date_temp, '%Y-%m-%d')
# rpt_date2 = date.strftime(date_temp2, '%Y-%m-%d')
# rpt_date3 = date.strftime(date_temp3, '%Y-%m-%d')
#
# items = 'symbol, date, rpt_date'
# table = 'stk_fina_calc'
# condition = ' where (date = \'' + rpt_date + '\' or date = \'' + rpt_date2 + '\' or date = \'' + rpt_date3 + '\') and symbol in (' + str(divSet).replace('[', '').replace(']', '') + ') order by symbol, date desc'
#
# quarter_data = get_all_data(items, table, condition)
# set_div_yield_remove = []
# valid_quarter_date = {}
# print(requestDate)
#
# for b in range(0, len(quarter_data), 3):
#     if quarter_data[b][2] is not None and requestDate > quarter_data[b][2].strftime('%Y-%m-%d'):
#         valid_quarter_date[quarter_data[b][0]] = quarter_data[b][1]
#     elif quarter_data[b + 1][2] is not None and requestDate > quarter_data[b + 1][2].strftime('%Y-%m-%d'):
#         valid_quarter_date[quarter_data[b][0]] = quarter_data[b + 1][1]
#     elif quarter_data[b + 2][2] is not  None and requestDate > quarter_data[b + 2][2].strftime('%Y-%m-%d'):
#         valid_quarter_date[quarter_data[b][0]] = quarter_data[b + 2][1]
#     else:
#         set_div_yield_remove.append(quarter_data[b][0])
# divSet = list(set(divSet).difference(set(set_div_yield_remove)))

# for i in range(0, len(stk_list), 10):
#     start_date = stk_ipo[stk_list[i]].strftime('%Y-%m-%d')
#     if start_date < '2010-01-01':
#         start_date = '2010-01-01'
#     try:
#         wind_data = w.wsd(stk_list[i:i+10], "pb_lf", start_date, "2018-03-18",  "")
#         for g in range(0,len(wind_data.Codes)):
#             for k in range(0, len(wind_data.Times)):
#                 if np.isnan(wind_data.Data[0][k]):
#                     continue
#                 update_sql = 'update data.stk_ratio where symbol =\'' + wind_data.Codes[g] + '\' and date = \'' + wind_data.Times[k].strftime('%Y-%m-%d') + '\' set pb = \'' + str(wind_data.Data[g][k]) + '\')'
#                 print(update_sql)
# items = 'symbol, pe_ttm'
# table = 'stk_ratio'
# condition = ' where date = \'' + requestDate + '\' and symbol in (' + str(divSet).replace('[', '').replace(']',
#                                                                                                            '') + ') order by symbol'
# pe_data = get_all_data(items, table, condition)
# set_pe_remove = []
# for e in range(0, len(pe_data)):
#     if pe_data[e][1] >= PE or pe_data[e][1] <= 0:
#         set_pe_remove.append(pe_data[e][0])
#
# divSet = list(set(divSet).difference(set(set_pe_remove)))

# date_temp = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-1).date()
# date_temp2 = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-2).date()
# rpt_date = date.strftime(date_temp, '%Y-%m-%d')
# rpt_date2 = date.strftime(date_temp2, '%Y-%m-%d')
#
# items = 'symbol, date, rpt_date'
# table = 'stk_fina_calc'
# condition = ' where (date = \'' + rpt_date + '\' or date = \'' + rpt_date2 +'\') and symbol in (' + str(divSet).replace('[', '').replace(']', '') + ') order by symbol, date desc'
#
# quarter_data = get_all_data(items, table, condition)
# set_div_yield_remove = []
# valid_quarter_date = {}
# # setValue_marketCap = w.wsd(divSet, "mkt_cap_ashare2", requestDate, requestDate,"unit=1;currencyType=;TradingCalendar=SZSE")
# for b in range(0, len(quarter_data), 2):
#     if quarter_data[b][2] is not None and requestDate > quarter_data[b][2].strftime('%Y-%m-%d'):
#         valid_quarter_date[quarter_data[b][0]] = quarter_data[b][1]
#     elif quarter_data[b][2] is None or requestDate > quarter_data[b+1][2].strftime('%Y-%m-%d'):
#         valid_quarter_date[quarter_data[b][0]] = quarter_data[b+1][1]
#     else:
#         set_div_yield_remove.append(quarter_data[b][0])
# divSet = list(set(divSet).difference(set(set_div_yield_remove)))

# set_roe_value_avg = []
# set_roe_remove = []
# set_roe = {}
#
# for c in range(0, len(divSet)):
#     end_date = valid_quarter_date[divSet[c]]
#     temp_date = arrow.get(end_date).replace(years=-3).date()
#     end_date = date.strftime(end_date, '%Y-%m-%d')
#     start_date = date.strftime(temp_date, '%Y-%m-%d')
#     items = 'roe_ttm'
#     table = 'stk_fina_calc'
#     condition = ' where symbol = \'' + divSet[c] + '\'  and date between \'' + start_date + '\' and \'' + end_date + '\' and roe_ttm is not null order by date asc'
#
#     roe_data = get_all_data(items, table, condition)
#     if len(roe_data) < 7:
#         set_roe_remove.append(divSet[c])
#         continue
#
#     e_avg_temp = 1  # 计算三年ROE指数平均值
#     for roe_q in roe_data:
#         e_avg_temp = e_avg_temp * (1 + roe_q[0] / 100)
#
#     if e_avg_temp <= 1:  # 三年ROE指数平均值低于1直接淘汰
#         set_roe_remove.append(divSet[c])
#         continue
#     set_roe_value_avg.append(100 * (float(e_avg_temp) ** (1 / len(roe_data)) - 1))
#     set_roe[divSet[c]] = set_roe_value_avg[-1]
#
#     if set_roe_value_avg[-1] <= ROE or roe_data[c][-1] <= ROE:  # 三年ROE指数均值或最后一期ROE低于低于标准者剔除
#         set_roe_remove.append(divSet[c])
#         del set_roe[divSet[c]]
#
# divSet = list(set(divSet).difference(set(set_roe_remove)))
#     if div_yield_data[b][1] <= DIVIDEND_RATE:
#         set_div_yield_remove.append(div_yield_data[b][0])
# divSet = list(set(divSet).difference(set(set_div_yield_remove)))
# conn, cur = connDB()
# path = 'C:/Users/gjun/Downloads/PB3.txt'
# with open(path, 'r') as f:
#     for i in f:
#         b = i.strip().split(',')
#         del b[0]
#         if b[0].startswith('6'):
#             c = b[0] + '.SH'
#         else:
#             c = b[0] + '.SZ'
#         del b[0]
#         b.insert(0, c)
#         if b[2] == '':
#             continue
#         insert_sql = 'update data.stk_ratio set pb = \'' + b[2] + '\' where symbol = \'' + b[0] + '\' and date = \''+ b[1] + '\''
#         # print(insert_sql)
#         try:
#             cur.execute(insert_sql)
#
#         except Exception as e:
#             print(e)
#             print(insert_sql)
#     print(b[0] + b[1] + ' is inserted')
# conn.commit()

# conn, cur = connDB()
# path = 'D:/temp1/'
# for filename in os.listdir(path):
#     stockprice = open(path + filename, mode='r', encoding=None, errors=None, newline=None, closefd=True,
#                       opener=None)
#     content = stockprice.readlines()
#     for i in content:
#         a = i.strip().replace('SHA','SH').split(',')
#         # print(a)
#         update_sql = 'update data.stk_ratio set pb =\'' + str(a[1]) + '\' where symbol = \'' +a[0] + '\' and date  = \'' + a[2] + '\''
#         if a[2] > '2018-03-16' or a[2] < '2010-01-01' :
#             update_sql = 'insert into data.stk_ratio (symbol, pb, date) values (' + str(a).replace('[','') .replace(']','') + ')'
#         # print(update_sql)
#         try:
#             cur.execute(update_sql)
#         except Exception as e:
#             print(e)
#             print(update_sql)
#     print(filename + ' is updated')
# conn.commit()


# A_wt=np.around(np.linspace(0,1,100),2)
# B_wt=np.around(np.linspace(0,1,100),2)
# C_wt=np.around(np.linspace(0,1,100),2)


#fac_weight=[[spr_weight,sto_weight,b_weight,d_weight,rp_weight,rs_weight] for spr_weight in spread_weight for sto_weight in stock_weight for b_weight in base_weight for d_weight in diff_weight  for rp_weight in rbp_weight for rs_weight in rbs_weight if spr_weight+sto_weight+b_weight+d_weight+rp_weight+rs_weight==1]
#fac_weight=DataFrame(fac_weight,columns=['spread_weight','stock_weight','base_weight','diff_weight','rbp_weight','rbs_weight']).T

# fac_weight=[[spread_wei,stock_wei,base_wei,diff_wei,rbp_wei,rbs_wei] for spread_wei in spread_weight for stock_wei in stock_weight for base_wei in base_weight for diff_wei in diff_weight for rbp_wei in rbp_weight for  rbs_wei in rbs_weight if spread_wei+stock_wei+base_wei+diff_wei+rbp_wei+rbs_wei==1]
# fac_weight=DataFrame(fac_weight,columns=['spread_weight','stock_weight','base_weight','d

# weight =  [[a,b,c] for a in A_wt for b in B_wt for c in C_wt if a + b + c == 1]
# weight = DataFrame(weight, columns= ['A','B','C'])
# weight.to_csv('test.csv')
# table = 'stk_price_forward'
# type = 'qfq'
# conn, cur = connDB()
# items = 'symbol, max(date) as date'
# tables = table
# condition = ' group by symbol order by symbol'
# data_info = get_all_data(items, tables, condition)
# edate = datetime.now().date().strftime('%Y-%m-%d')
#
# for k in range(0, len(data_info)):
#     sdate = (data_info[k][1] + timedelta(days = 1)).strftime('%Y-%m-%d')
#     if sdate > edate:
#        continue
#     try:
#         pricedata = ts.get_k_data(data_info[k][0].replace('.SH','').replace('.SZ',''), ktype='D', autype=type, start=sdate, end=edate);
#         del pricedata['volume']
#         print(pricedata)
#     except Exception as e:
#         print(e)
#
#     for h in range(0, len(pricedata)):
#         if data_info[k][0].startswith('6'):
#             values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SH\'')
#         else:
#             values = str(pricedata.values[h].tolist()).replace('[', '').replace('\']', '.SZ\'')
#         insql = 'insert into data. ' + table + ' (date,open,close,high,low,symbol) values (' + values + ');'
#         # print(insql)
#         try:
#             conn.cursor().execute(insql)
#         except Exception as e:
#             print(e)
#
#     conn.commit()
#     print(str(data_info[k][0]) + ' is inserted' )
# connClose(conn, cur)
# conn, cur = connDB()
# items = 'symbol,  max(date) as date'
# tables = 'etf_price_backward'
# condition = ' group by symbol order by symbol'
# data_info = get_all_data(items, tables, condition)
# etf_info = dict(data_info)
# end_date = datetime.now().strftime('%Y-%m-%d')
w.start()
# for i in etf_info:
#     start_date = (etf_info[i] + timedelta(1)).strftime('%Y-%m-%d')
#     if start_date > end_date:
#         continue
#     etf_price = w.wsd(i, "close,pct_chg", start_date, end_date, "PriceAdj=B")
#     for r in range(0, len(etf_price.Times)):
#         etf_value = tuple([etf_price.Codes[0], etf_price.Times[r].strftime('%Y-%m-%d'), etf_price.Data[0][r], etf_price.Data[1][r]])
#         insert_sql = 'insert into data.etf_price_backward values ' + str(etf_value)
#         try:
#             conn.cursor().execute(insert_sql)
#         except Exception as e:
#             print(e)
#     print(i + ' is inserted. ')
#     conn.commit()
# connClose(conn, cur)

# conn, cur = connDB()
# items = 'symbol'
# tables = 'stk_info'
# condition = '  order by symbol'
# data_info = get_all_data(items, tables, condition)
# symbol = []
# for i in data_info:
#     w_data = w.wsd(i[0], "indexcode_wind", "2018-04-09", "2018-04-09", "industryType=4")
#     print(i[0])
#     if w_data.Data[0][0] == None:
#         continue
#     insert_sql = 'update data.stk_info set index_code =\'' + w_data.Data[0][0] + '\' where symbol = \'' + i[0] + '\''
#     insert_sql = insert_sql.replace('\'default\'','default')
#     print(insert_sql)
#     try:
#         conn.cursor().execute(insert_sql)
#     except Exception as e:
#         print(e)
#     print(i[0] + ' is inserted. ')
#     conn.commit()
#
# connClose(conn, cur)

# w.start()
# conn, cur = connDB()
# # items = 'symbol, max(date)'
# # tables = 'stk_adj_factor'
# # condition = ' order by symbol'
#
# items = 'symbol, ipo'
# tables = 'stk_info'
# condition = ' where symbol not in (select symbol from stk_adj_factor group by symbol) order by symbol'
#
# data_info = get_all_data(items, tables, condition)
# stk_data = dict(data_info)
# end_date = datetime.now().date().strftime('%Y-%m-%d')
#
# for i in stk_data:
#     start_date = (stk_data[i] + timedelta(1)).strftime('%Y-%m-%d')
#     if start_date > end_date:
#         continue
#     w_data = w.wsd(i, "adjfactor", start_date, end_date, "")
#
#     for s in range(0, len(w_data.Times)):
#         insert_sql = 'insert into data.stk_adj_factor values(\'' + i + '\', \'' + w_data.Times[s].strftime('%Y-%m-%d') +'\',\'' + str(w_data.Data[0][s]) + '\');'
#         # print(insert_sql)
#         try:
#             conn.cursor().execute(insert_sql)
#         except Exception as e:
#             print(e)
#     print(i + ' is inserted. ')
#     conn.commit()
# connClose(conn, cur)

# ['000002.SZ', '000333.SZ', '000423.SZ', '000828.SZ', '002142.SZ', '002595.SZ', '600104.SH', '600388.SH', '600563.SH',
 # '600987.SH', '603369.SH']

# a = w.wsd("000002.SZ, 000333.SZ, 600987.SH", "trade_status", "2018-04-18", "2018-04-18", "")
# print(a)

from ConnectDB import connDB, connClose

conn, cur = connDB()
startDate = '2018-01-02'
endDate ='2018-04-24'
symbol = 'IF1806.CFE'

query_sql = 'select datetime, open from data.fur_price where symbol =\'' + symbol + '\' and datetime like \'%09:30:00\' and datetime between \'' + startDate + ' 09:30:00\' and \'' + endDate + ' 14:59:00\' order by datetime asc'
try:
    cur.execute(query_sql)
    cfe_open = cur.fetchall()
except Exception as e:
    print(e)

query_sql_2 = 'select datetime, close from data.fur_price where symbol =\'' + symbol + '\' and datetime like \'%14:59:00\' and datetime between \'' + startDate + ' 09:30:00\' and \'' + endDate + ' 14:59:00\' order by datetime asc'
try:
    cur.execute(query_sql_2)
    cfe_close = cur.fetchall()
except Exception as e:
    print(e)

open_data = {}
for i in cfe_open:
    open_data[i[0].date().strftime('%Y-%m-%d')] = float(i[1])

close_data = {}
for j in cfe_close:
    close_data[j[0].date().strftime('%Y-%m-%d')] = float(j[1])

chg_rate = []
for k in open_data:
    temp_chg = (close_data[k] - open_data[k]) / close_data[k] *100
    chg_rate.append(temp_chg)

connClose(conn, cur)