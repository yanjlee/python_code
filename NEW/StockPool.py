# -*- coding: utf-8 -*-
"""
@author: GuoJun
"""
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ConnectDB import get_all_data
import arrow
import cProfile
from math import exp
import pandas as pd


#############################
# 常量设置
PE = 25 # 最大PE
PB = 5 # 最大PB
ROE = 15 # 最小ROE
DIVIDEND_RATE = 1.5 # 最小股息率
MKT_CAP = 5000000000 # 最小市值
TOP_STOCK_NUMBER = 100

# requestDate = '2018-12-26'
#############################

def get_stock_list(requestDate):
    # 1. 过滤东三省和黑名单b_list公司，获取获取symbol和IPO日期
    items = 'symbol, ipo'
    table = 'stk_info'
    condition = ' where area not in (\'黑龙江\',\'吉林\',\'辽宁\') and symbol not in (select symbol from data.b_list) and symbol in (select symbol from data.idx_meb)'
    ipo_data = get_all_data(items, table, condition)

    divSet= []

    # 2. IPO日期过滤掉上市时间低于3年的公司
    for a in range(0, len(ipo_data)):
        if ipo_data[a][1] < datetime.date(datetime.strptime(requestDate, '%Y-%m-%d') - relativedelta(years=3)):
            divSet.append(ipo_data[a][0])

    # divSet = list(set(divSet).difference(set(set_ipo_remove)))
    # divSet = list(set(divSet).symmetric_difference(set(set_ipo_remove)))

    # 3. 过滤掉总市值低于特定值公司，排除小市值公司策略的干扰
    items = 'symbol'
    table = 'stk_price'
    condition = 'where mktcap > ' + str(MKT_CAP) + ' and date =\'' + requestDate +'\' order by symbol'
    mkt_data = get_all_data(items, table, condition)
    divSet1 = str(mkt_data).replace(',), (',',').replace('((','(').replace(',))',')')

    # 4. PE值过滤
    items = 'symbol'
    table = 'stk_ratio'
    condition = 'where symbol in ' + divSet1 + ' and pe_ttm > 0 and pe_ttm <= ' + str(PE) + ' and date = \'' + requestDate + '\' order by symbol'
    pe_data = get_all_data(items, table, condition)
    divSet2 =  str(pe_data).replace(',), (',',').replace('((','(').replace(',))',')')


    # 5. 股息收益率要大于5年国债收益率
    items = 'a.symbol'
    table = 'stk_fina_calc'
    condition = ' a inner join (SELECT symbol, max(date) as date FROM data.stk_fina_calc' \
                ' where rpt_date <= \'' + requestDate + '\' and symbol in ' + divSet2 + \
                ' group by symbol) b on a.symbol =b.symbol and a.date = b.date where a.div_yield > ' + str(DIVIDEND_RATE) + ' order by a.symbol'
    div_yield_data = get_all_data(items, table, condition)
    divSet3 = str(div_yield_data).replace(',), (',',').replace('((','(').replace(',))',')')


    # 6. 3年平均ROE过滤与排序
    items = 'symbol, max(date)'
    table = 'stk_fina_calc'
    condition = ' where symbol in ' + divSet3 + ' and rpt_date < \'' + requestDate + '\' group by symbol order by symbol'
    quarter_data = get_all_data(items, table, condition)
    divSet4= dict(quarter_data)

    set_roe_value_avg = []
    set_roe_remove = []
    set_roe = {}
    for k, v in divSet4.items():
        end = v.strftime('%Y-%m-%d')
        start = arrow.get(v).replace(years=-3).date().strftime('%Y-%m-%d')
        items = 'roe_ttm'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + k + '\'  and date between \'' + start + '\' and \'' + end + '\' and roe_ttm is not null order by date asc'
        roe_data = get_all_data(items, table, condition)
        if len(roe_data) < 7:
            set_roe_remove.append(k)
            continue

        e_avg_temp = 1  # 计算3年ROE指数平均值
        for roe_q in roe_data:
            e_avg_temp = e_avg_temp * (1 + roe_q[0] / 100)
            if roe_q[0] < ROE: ## 任何一期低于标准，淘汰
                set_roe_remove.append(k)
        if e_avg_temp <= 1:  # 3年ROE指数平均值低于1直接淘汰
            set_roe_remove.append(k)
            continue
        set_roe_value_avg.append(100 * (float(e_avg_temp) ** (1 / len(roe_data)) - 1))
        set_roe[k] = set_roe_value_avg[-1]

        if set_roe_value_avg[-1] <= ROE or roe_data[-1][-1] <= ROE:  # 3年ROE指数均值或最后一期ROE低于低于标准者剔除
            set_roe_remove.append(k)
            del set_roe[k]
    divSet5 = list(set(list(divSet4.keys())).difference(set(set_roe_remove)))

    # 7. 比率筛选：3年ROE均值/PB现值需大于5
    roe_std = {}
    roe_to_pb = {} # 经济学意义： 100* NI / MarketValue， 值越高越好，低值表明赚钱能力过低，MV可以约等于Asset
    roe_std_to_pb = {}
    std_to_roe = {}
    set_std_remove = []
    for k in divSet5:
        end2 = divSet4[k].strftime('%Y-%m-%d')
        start2 = arrow.get(divSet4[k]).replace(years=-3).date().strftime('%Y-%m-%d')
        items = 'roe_ttm'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + k + '\'  and date between \'' + start2 + '\' and \'' + end2 + '\' and roe_ttm is not null order by date asc'
        roe_data = get_all_data(items, table, condition)
        roe_ttm_list = []
        for j in roe_data:
            roe_ttm_list.append(float(j[0]))
        roe_std[k] = float(np.std(roe_ttm_list))

        item2 = 'pb'
        table2 = 'stk_ratio'
        condition2 = ' where symbol = \'' + k + '\' order by date desc limit 1'
        pb_data = get_all_data(item2, table2, condition2)
        pb_v = float(pb_data[0][0])
        if len(pb_data) == 0 or pb_v < 0 or pb_v > PB or set_roe[k] / pb_v < 5: ##  PB需要大于1，否则RI(留存收益）为负
            set_std_remove.append(k)
            roe_std.pop(k)
            continue
        elif roe_std[k] / pb_v > 3:
            set_std_remove.append(k)
            roe_std.pop(k)
            set_roe.pop(k)
            continue
        else:
            roe_std_to_pb[k] = roe_std[k] / pb_v
            roe_to_pb[k] = set_roe[k] / pb_v
            std_to_roe[k] = roe_std[k] / set_roe[k]
    divSet6 = list(set(divSet5).difference(set(set_std_remove)))

    ## Sort them, ln 自然对数计算
    roe_std_to_pb = dict(sorted(roe_std_to_pb.items(), key=lambda x: x[1], reverse=False)) # 一定范围
    roe_to_pb = dict(sorted(roe_to_pb.items(), key=lambda x: x[1], reverse=False)) # 越大越好
    set_roe = {k: v for k, v in set_roe.items() if k in divSet6}
    set_roe = dict(sorted(set_roe.items(), key=lambda x: x[1], reverse=True)) # 越大越好
    std_to_roe = dict(sorted(std_to_roe.items(), key=lambda x: x[1], reverse=False)) # 越小越好

    roe_to_pb_ln = {}
    roe_ln ={}
    roe_std_to_pb_ln = {}
    std_to_roe_ln = {}

    min_roe2pb = sorted(roe_to_pb.values())[0]
    min_roe = sorted(set_roe.values())[0]
    max_std2roe =  sorted(std_to_roe.values())[-1]
    max_std2pb = sorted(roe_std_to_pb.values())[-1]

    for k in divSet6:
        roe_to_pb_ln[k] = exp(min_roe2pb/roe_to_pb[k])
        roe_ln[k] = exp(min_roe/set_roe[k])
        roe_std_to_pb_ln[k] = exp(roe_std_to_pb[k]/max_std2pb)
        std_to_roe_ln[k] = exp(std_to_roe[k]/max_std2roe)

    ## 综合排序,　值小越越好
    roe_order = {}
    for j in divSet6:
        roe_order[j] = round(roe_to_pb_ln[j] * 0.4 + roe_ln[j] * 0.3 + 0.1 * roe_std_to_pb_ln[j] + 0.2 * std_to_roe_ln[j],3)
    roe_order_list = dict(sorted(roe_order.items(), key=lambda x: x[1], reverse=False))
    print(roe_order_list)
    df = pd.DataFrame(list(roe_order_list.items()), columns=['symbol','score'])
    df = df.set_index('symbol')
    divSet7 = list(roe_order_list.keys())

    # 8. 输出
    if len(divSet7) > 1:
        order_list = []
        if len(divSet7) > TOP_STOCK_NUMBER:
            order_list = divSet7[:TOP_STOCK_NUMBER]
            order_list.sort()
        else:
            order_list = divSet7
    elif len(divSet7) == 1:
        order_list = divSet7
    else:
        order_list = []
    return(order_list, divSet7, df)

def get_info(divSet7):
    items = 'symbol, name, industry'
    table = 'stk_info'
    condition = 'where symbol in ' + str(divSet7).replace('[', '(').replace(']', ')')
    stk_data = get_all_data(items, table, condition)
    df = pd.DataFrame(list(stk_data),columns= ['symbol','name','industry'])
    df =df.set_index('symbol')
    return (df)

order, divSet7, df = get_stock_list('2019-04-25')

df_info = get_info(divSet7)
df = pd.merge(df,df_info,left_index=True,right_index=True)
print(get_info(order))
# # # #
# list_2 = stock_list('2018-07-05')
# cProfile.run("stock_list('2018-05-04')")

print(order)
print(df.sort_values(axis = 0,by = 'industry'))
print(df_info)