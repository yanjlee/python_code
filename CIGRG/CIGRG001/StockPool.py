# -*- coding: utf-8 -*-
"""
@author: GuoJun
"""
import logging as log
import datetime
import numpy as np
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from ConnectDB import connDB, connClose, get_data, get_all_data
import arrow
import cProfile
from math import log as lg, exp

# BASE_DIR = os.path.dirname(__file__)
# LOG_PATH = BASE_DIR +'/log/data_update/'
# LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))) + '.log'
log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")
#############################
# 常量设置
PE = 30
PB = 3
ROE = 15
DIVIDEND_RATE = 1
WEIGHT = 0.95
MKT_CAP = 15000000000
TOP_STOCK_NUMBER = 10

# requestDate = '2018-07-05'
#############################


def stock_list(requestDate):
    items = 'symbol, ipo'
    table = 'stk_info'
    condition = ' where area not in (\'黑龙江\',\'吉林\',\'辽宁\')'
    ipo_data = get_all_data(items, table, condition)

    divSet= []
    # IPO日期过滤掉上市时间低于3年的公司

    for a in range(0, len(ipo_data)):
        if ipo_data[a][1] < datetime.date(datetime.strptime(requestDate, '%Y-%m-%d') - relativedelta(years=3)):
            divSet.append(ipo_data[a][0])

    # divSet = list(set(divSet).difference(set(set_ipo_remove)))
    # divSet = list(set(divSet).symmetric_difference(set(set_ipo_remove)))

    # 过滤掉总市值低于特定值公司，排除小市值公司策略的干扰
    items = 'symbol, mktcap'
    table = 'stk_price'
    condition = ' where date = \'' + requestDate + '\' and symbol in (' + str(divSet).replace('[','').replace(']','') + ') order by symbol'
    mkt_data = get_all_data(items, table, condition)
    set_marketCap_remove = []

    # setValue_marketCap = w.wsd(divSet, "mkt_cap_ashare2", requestDate, requestDate,"unit=1;currencyType=;TradingCalendar=SZSE")
    for b in range(0, len(mkt_data)):
        if mkt_data[b][1] <= MKT_CAP:
            set_marketCap_remove.append(mkt_data[b][0])
    divSet1 = list(set(divSet).difference(set(set_marketCap_remove)))

    # 过滤掉非正常状态的公司

    # PE值过滤
    items = 'symbol, pe_ttm'
    table = 'stk_ratio'
    condition = ' where date = \'' + requestDate + '\' and symbol in (' + str(divSet1).replace('[', '').replace(']', '') + ') and pe_ttm is not null order by symbol'
    pe_data = get_all_data(items, table, condition)
    set_pe_remove = []
    for e in range(0, len(pe_data)):
        if pe_data[e][1] >= PE or pe_data[e][1] <= 0:
            set_pe_remove.append(pe_data[e][0])

    divSet2 = list(set(divSet1).difference(set(set_pe_remove)))


    # 股息收益率要大于5年国债收益率
    # date_temp = arrow.get(requestDate, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-1).date()
    # rpt_date = date.strftime(date_temp, '%Y-%m-%d')
    items = 'a.symbol, a.div_yield'
    table = 'stk_fina_calc'
    condition = ' a inner join (SELECT symbol, max(date) as date FROM data.stk_fina_calc group by symbol) b on a.symbol =b.symbol and a.date = b.date where a.symbol in (' + str(divSet2).replace('[', '').replace(']','') + ') and a.div_yield > 0 order by a.symbol'
    div_yield_data = get_all_data(items, table, condition)
    set_div_yield_remove = []

    # setValue_marketCap = w.wsd(divSet, "mkt_cap_ashare2", requestDate, requestDate,"unit=1;currencyType=;TradingCalendar=SZSE")
    for b in range(0, len(div_yield_data)):
        if div_yield_data[b][1] <= DIVIDEND_RATE:
            set_div_yield_remove.append(div_yield_data[b][0])
    divSet3 = list(set(divSet2).difference(set(set_div_yield_remove)))


    # 3年平均ROE过滤与排序
    # setValue_roe_reportDate = w.wsd(divSet, "latelyrd_bt", requestDate, requestDate,"Period=Q;Days=Alldays;Fill=Previous")  # 获取有效报表日期，避免未来数据
    set_div_yield_remove_2 = []
    valid_quarter_date = {}
    for k in divSet3:
        items = 'max(date)'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + k + '\' and rpt_date < \'' + requestDate + '\' order by date desc'
        quarter_data = get_all_data(items, table, condition)
        if len(quarter_data) == 0:
            set_div_yield_remove_2.append(k)
        else:
            valid_quarter_date[k] = quarter_data[0][0]

    divSet4 = list(set(divSet3).difference(set(set_div_yield_remove_2)))


    set_roe_value_avg = []
    set_roe_remove = []
    set_roe = {}
    for c in range(0, len(divSet4)):
        end_date = valid_quarter_date[divSet4[c]]
        temp_date = arrow.get(end_date).replace(years=-3).date()
        end_date = date.strftime(end_date, '%Y-%m-%d')
        start_date = date.strftime(temp_date, '%Y-%m-%d')
        items = 'roe_ttm'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + divSet4[c] + '\'  and date between \'' + start_date + '\' and \'' + end_date + '\' and roe_ttm is not null order by date asc'

        roe_data = get_all_data(items, table, condition)
        if len(roe_data) < 7:
            set_roe_remove.append(divSet4[c])
            continue

        e_avg_temp = 1  # 计算3年ROE指数平均值
        for roe_q in roe_data:
            e_avg_temp = e_avg_temp * (1 + roe_q[0] / 100)
            if roe_q[0] < ROE: ## 任何一期低于标准，淘汰
                set_roe_remove.append(divSet4[c])

        if e_avg_temp <= 1:  # 3年ROE指数平均值低于1直接淘汰
            set_roe_remove.append(divSet4[c])
            continue
        set_roe_value_avg.append(100 * (float(e_avg_temp) ** (1 / len(roe_data)) - 1))
        set_roe[divSet4[c]] = set_roe_value_avg[-1]

        if set_roe_value_avg[-1] <= ROE or roe_data[-1][-1] <= ROE:  # 3年ROE指数均值或最后一期ROE低于低于标准者剔除
            set_roe_remove.append(divSet4[c])
            del set_roe[divSet4[c]]
    divSet5 = list(set(divSet4).difference(set(set_roe_remove)))

    # 3年ROE均值/PB现值需大于5
    roe_std = {}
    roe_to_pb = {} # 经济学意义： 100* NI / MarketValue， 值越高越好，低值表明赚钱能力过低，MV可以约等于Asset
    roe_std_to_pb = {}
    std_to_roe = {}
    set_std_remove = []
    for d in divSet5:
        end_date = valid_quarter_date[d]
        temp_date = arrow.get(end_date).replace(years=-3).date()
        end_date = date.strftime(end_date, '%Y-%m-%d')
        start_date = date.strftime(temp_date, '%Y-%m-%d')
        items = 'roe_ttm'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + d + '\'  and date between \'' + start_date + '\' and \'' + end_date + '\' and roe_ttm is not null order by date asc'
        roe_data = get_all_data(items, table, condition)
        roe_ttm_list = []
        for j in roe_data:
            roe_ttm_list.append(float(j[0]))
        roe_std[d] = float(np.std(roe_ttm_list))

        item2 = 'pb'
        table2 = 'stk_ratio'
        condition2 = ' where symbol = \'' + d + '\'  and date = \'' + requestDate + '\''
        pb_data = get_all_data(item2, table2, condition2)
        if len(pb_data) == 0 or float(pb_data[0][0]) < 1 or float(pb_data[0][0]) > 50 or set_roe[d] / float(pb_data[0][0]) < 4 or set_roe[d] / float(pb_data[0][0]) > 30: ##  PB需要大于1，否则RI(留存收益）为负
            set_std_remove.append(d)
            roe_std.pop(d)
            continue
        elif roe_std[d] / float(pb_data[0][0]) > 3:
            set_std_remove.append(d)
            roe_std.pop(d)
            set_roe.pop(d)
            continue
        else:
            roe_std_to_pb[d] = roe_std[d] / float(pb_data[0][0])
            roe_to_pb[d] = set_roe[d] / float(pb_data[0][0])
            std_to_roe[d] = roe_std[d] / set_roe[d]

    divSet6 = list(set(divSet5).difference(set(set_std_remove)))

    roe_std_to_pb = sorted(roe_std_to_pb.items(), key=lambda x: x[1], reverse=False)
    roe_to_pb = sorted(roe_to_pb.items(), key=lambda x: x[1], reverse=False)
    set_roe = {k: v for k, v in set_roe.items() if k in divSet6}
    set_roe = sorted(set_roe.items(), key=lambda x: x[1], reverse=True)
    std_to_roe = sorted(std_to_roe.items(), key=lambda x: x[1], reverse=False)

    roe_to_pb_ln = {}
    for i in roe_to_pb:
        roe_to_pb_ln[i[0]] = exp(roe_to_pb[0][1]/i[1])

    roe_ln ={}
    for k in set_roe:
        roe_ln[k[0]] = exp(set_roe[-1][1]/k[1])

    roe_std_to_pb_ln = {}
    for h in roe_std_to_pb:
        roe_std_to_pb_ln[h[0]] = exp(h[1]/roe_std_to_pb[-1][1])

    std_to_roe_ln = {}
    for m in std_to_roe:
        std_to_roe_ln[m[0]] = exp(m[1]/std_to_roe[-1][1])

    roe_order = {}
    for j in roe_ln.keys():
        roe_order[j] = (roe_to_pb_ln[j] + roe_ln[j]) * 0.618 + 0.382 * (roe_std_to_pb_ln[j] + std_to_roe_ln[j])

    roe_order_list = sorted(roe_order.items(), key=lambda x: x[1], reverse=False)
    roe_list = []
    for g in roe_order_list:
        roe_list.append(g[0])

    divSet7 = roe_list
    # divSet7 = divSet6


    if len(divSet7) > 1:
        # ## EMA filter for trading prices
        # items = 'a.symbol'
        # table = 'stk_price_forward a inner join stk_price_tec b on a.symbol =b.symbol and a.date=b.date '
        # condition = 'where a.date = \'' + requestDate + '\' and a.symbol in (' + str(roe_list).replace('[', '').replace(
        #     ']',
        #     '') + ') and (0.5*a.close+0.3*a.open+0.1*a.high+0.1*a.low) > b.ema21 and (0.5*a.close+0.3*a.open+0.1*a.high+0.1*a.low) > b.ema55 order by a.symbol'
        # symbol_data = get_all_data(items, table, condition)
        #
        # symbol_list = []
        # for kk in symbol_data:
        #     symbol_list.append(kk[0])
        #
        # divSet7 = symbol_list

    # ### 获取停牌的股票，剔除
    #         w.start()
    #         w_data = w.wsd(divSet7, "trade_status", requestDate, requestDate, "")
    #         # print(w_data)
    #         for st in range(len(w_data.Codes)):
    #             if w_data.Data[0][st] != '交易':
    #                 divSet7.remove(w_data.Codes[st])

        # queue_list = {}
        # for k in divSet7:
        #     queue_list[k] = roe_std[k] / set_roe[k]
        #
        # set_order_stock = sorted(queue_list.items(), key=lambda d: d[1], reverse=False)
        # order_list = []
        # for stock in set_order_stock:
        #     order_list.append(stock[0])

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

    return(order_list, divSet7)
# # # #
# list_2 = stock_list('2018-07-05')
# log.info(list_2)
# # cProfile.run("stock_list('2018-05-04')")