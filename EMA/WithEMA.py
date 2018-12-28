

# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from CIGRG.CIGRG001.StockPool import stock_list
from datetime import datetime
import pandas as pd
from ConnectDB import get_all_data
import prettytable as pt
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import requests
import re


def calc_return(stock_id, start_date, end_date, trade_loss):

    # 给持有或者卖出的交易信号，计算手续费和滑点外，计算出收益情况。
    # stock_id = '002456.SZ'
    # start_date = '2018-01-01'
    # end_date = '2018-06-25'
    # trade_loss = 0.001
    items = 'a.symbol, a.date, a.open, a.close, b.ema5, b.ema21, b.ema55,b.atr13, a.high,a.low'
    table = 'stk_price_forward a inner join stk_price_tec b on a.symbol =b.symbol and a.date=b.date '
    condition = 'where a.symbol = \'' + stock_id + '\' and a.date >= \'' + start_date + '\' and a.date <= \'' + end_date + '\' order by date asc'
    symbol_data = get_all_data(items, table, condition)

    # 生成交易信号，添加到最后一列
    price_data = []
    for price in symbol_data:
        temp = []
        if price[3] <= price[5] or price[3] <= price[6]: # close<= ema21或者ema55，都保持空仓状态
            signal = 0
        # elif max(price[2], price[3]) <= price[4]:
        elif (Decimal(0.1) * (price[8] + price[9]) + Decimal(0.3) * price[2]+ Decimal(0.5) * price[3]) <= price[4]:
            signal = 0
        else:
            signal = 1

        temp.append(signal)
        price_data.append(temp)

    # 计算交易后的回报
    price_data[0].append(0)
    price_data[1].append(0)
    for k in range(2, len(symbol_data)):
        if price_data[k-1][0] == 1 and price_data[k-2][0] == 1: #前两日都是持股状态的日收益
            current_return = round(100 *(symbol_data[k-1][3] - symbol_data[k-2][3]) / symbol_data[k-1][3],3)
        elif price_data[k-1][0] == 1 and price_data[k-2][0] == 0: #买入日收益——当日开收盘差价
            current_return = round(100 *(symbol_data[k][3] - symbol_data[k][2]) / symbol_data[k][2],3)
        elif price_data[k-1][0] == 0 and price_data[k-2][0] == 1: #卖出日收益，当日开盘与前一收盘价差
            current_return = round(100 *(symbol_data[k][2] - symbol_data[k-1][3]) / symbol_data[k-1][3],3)
        else:
            current_return = 0
        price_data[k].append(current_return)

    # 计算累计回报
    price_data[0].append(1)
    cl_return = [1]
    for j in range(1, len(symbol_data)):
        if price_data[j-1][0] != price_data[j][0]:
            current_cl_return = round(price_data[j - 1][2] * (1 + Decimal(price_data[j][1] / 100) - Decimal(trade_loss)), 3)
        else:
            current_cl_return = round(price_data[j - 1][2] * (1 + Decimal(price_data[j][1] / 100)), 3)
        cl_return.append(current_cl_return)
        price_data[j].append(current_cl_return)

    # 计算最大回撤
    price_data[0].append(0)
    for x in range(1,len(price_data)):
        temp = round((cl_return[x] - max(cl_return[0:x])) / max(cl_return[0:x]), 3)
        if temp <= 0:
            price_data[x].append(temp)
        else:
            price_data[x].append(0)

    # 计算持有股票不操作的日收益
    price_data[0].append(1)
    for i in range(1, len(symbol_data)):
        temp_rate = round(symbol_data[i][3]/symbol_data[0][3],3)
        price_data[i].append(temp_rate)

    # 拼合DataFrame

    for j in range(0,len(price_data)):
        price_data[j][0:0] = symbol_data[j][0:2]

    pd_dt =pd.DataFrame(price_data, columns=['symbol','date','signal','daily_return','cl_return','max_dd','close_stk'])

    return(pd_dt)

def draw_return(pd_dt):
    x = np.array(pd_dt['date'])
    y1 = np.array(pd_dt['close_stk'])
    y2 = np.array(pd_dt['cl_return'])
    y3 = np.array(pd_dt['max_dd'])
    plt.figure(figsize=(9, 6))

    ## 收益子图
    plt.subplot(211)
    plt.plot(x, y1, 'b', label='close_stk')
    plt.plot(x, y2, 'r', label='cl_return', linewidth=1)
    plt.grid(True)
    plt.axis('tight')
    plt.ylabel('Return')
    pic_txt = 'Cumulative Return for Cigrg_007: ' + start_date + ' ~ ' + end_date + ', ' + str(pd_dt['cl_return'][-1])
    plt.legend(loc='upper left', frameon=False)
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=11.5, weight='bold')
    plt.title(pic_txt, loc='left', fontproperties=font_set)
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)  ## 隐藏第一框图横坐标

    ## 最大回撤子图
    plt.subplot(212)
    plt.plot(x, y3, 'b')
    # plt.xticks(rotation=30)
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('Date')
    plt.ylabel('MaxDrawDown')
    y_scale = float(min(list(pd_dt['max_dd'])))
    plt.ylim(y_scale, 0)

    PNG_FILENAME = 'CIGRG_007_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
    plt.savefig(PNG_FILENAME)
    # plt.show()

def history_test():
    start_date = '2017-12-01'
    end_date = '2018-06-26'
    trade_loss = 0.001
    # stock_list = ['000651.SZ', '600398.SH', '000423.SZ', '600612.SH', '000002.SZ', '600066.SH', '000333.SZ', '600104.SH', '601318.SH', '002508.SZ', '600690.SH', '600340.SH', '002081.SZ', '600201.SH', '600816.SH', '600660.SH']  # stocks pool
    stocks_list= ['000002.SZ','000333.SZ','000423.SZ','000651.SZ','600066.SH','600104.SH','600340.SH','600398.SH','600612.SH','601318.SH',]
    # stocks_list = stock_list()
    pd_return = pd.DataFrame()

    for stock_id in stocks_list:
        pd_dt = calc_return(stock_id, start_date, end_date, trade_loss)
        pd_return[stock_id] = pd_dt['cl_return']

    pd_return['total_cl_return'] = pd_return.apply(lambda x: x.sum()/len(stocks_list), axis=1)

    pd_return = pd_return.replace(',', '', regex=True)
    pd_return = pd_return.replace('-', 'NaN', regex=True).astype('float')

    pic_txt = 'Cumulative Return for Cigrg_007: ' + start_date + ' ~ ' + end_date  + ', ' + str(pd_return['total_cl_return'].iloc[-1])
    pd_return.plot(title=pic_txt)
    plt.show()

# pd_dt = calc_return('002456.SZ')
# draw_return(pd_dt)

def get_current_stocks():

    items = 'max(date)'
    table = 'idx_price'
    condition = ' where symbol =\'000001.SH\' group by symbol'
    idx_data = get_all_data(items, table, condition)
    currentDate = idx_data[0][0].strftime('%Y-%m-%d')

    # currentDate = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    # currentDate = '2018-06-29'
    top_stocks, stocks = stock_list(currentDate)
    # stocks = get_stock_list(currentDate)
    items = 'a.symbol, b.ema5, b.ema21, b.ema55'
    table = 'stk_price_forward a inner join stk_price_tec b on a.symbol =b.symbol and a.date=b.date'
    condition = ' where a.symbol in (' + str(stocks).replace('[','').replace(']','') + ') and a.date = \'' + currentDate + '\' and (0.5 * a.close + 0.3 * a.open + 0.1* a.high + 0.1 * a.low) > b.ema21 and (0.5 * a.close + 0.3 * a.open + 0.1* a.high + 0.1 * a.low) > b.ema55 and (0.5 * a.close + 0.3 * a.open + 0.1* a.high + 0.1 * a.low) > b.ema5'
    symbol_data = get_all_data(items, table, condition)
    print(top_stocks)
    print(stocks)

    stk_data=pd.DataFrame(list(symbol_data),columns=['symbol','ema5','ema21','ema55'])
    stk_data.set_index(['symbol'], inplace=True)

    stk_list = []
    for i in symbol_data:
        if i[0].endswith('.SZ',6,9):
            stk_list.append('sz' + i[0].replace('.SZ',''))
        else:
            stk_list.append('sh' + i[0].replace('.SH',''))

    get_sina_url = 'http://hq.sinajs.cn/list=' + str(stk_list).replace('[','').replace(']','').replace('\'','').replace(' ','')
    get_current_data = requests.get(get_sina_url).text.split('var hq_str_')
    del get_current_data[0]

    trading_data  = []
    for i in get_current_data:
        temp = i.split(',')
        if temp[0].startswith('sz',0,3):
            temp[0] = re.sub('=.*','.SZ',temp[0].replace('sz',''))
        else:
            temp[0] = re.sub('=.*','.SH',temp[0].replace('sh',''))
        trading_data.append([temp[0],float(temp[1]),float(temp[4]),float(temp[5]),float(temp[3]), round(0.3*float(temp[1])+0.5*float(temp[3]) + 0.1*float(temp[4]) + 0.1*float(temp[5]), 3)])

    for k in trading_data:
        new_ema5 = round(Decimal(1/3) * Decimal(k[4]) + stk_data['ema5'][k[0]] * Decimal(2/3),3)
        new_ema21 = round(Decimal(2/22) * Decimal(k[4]) + stk_data['ema21'][k[0]] * Decimal(20/22),3)
        new_ema55 = round(Decimal(2/56) * Decimal(k[4]) + stk_data['ema55'][k[0]] * Decimal(54/56),3)
        k.extend([new_ema5, new_ema21,new_ema55])

    trade_data = pd.DataFrame(trading_data, columns = ['symbol','open','high','low','close','center','ema5','ema21','ema55'])
    # data[data['three']>5]
    td_1 = trade_data[trade_data['center']>trade_data['ema5']]
    td_2 = td_1[td_1['center']>td_1['ema21']]
    td_3 = td_2[td_2['center']>td_2['ema55']]

    if len(td_3) > 1:
        symbol_list = list(td_3['symbol'])
        items = 'symbol, name, industry'
        table = 'stk_info'
        condition = ' where symbol in (' + str(symbol_list).replace('[','').replace(']','') + ') '
        symbol_data = get_all_data(items, table, condition)
        tb_list = []
        for j in range(0, len(symbol_data)):
            tb_list.append([j, symbol_data[j][0], symbol_data[j][1], symbol_data[j][2]])
        tb = pt.PrettyTable()
        tb.field_names = ['No.', 'Symbol', 'Name', 'Industry']
        for stock in tb_list:
            tb.add_row(stock)
        tb.align = 'l'
        print(tb)
    else:
        tb = ''
        symbol_list = ['All shares should be sold!']
        print('All shares should be sold!')

    return symbol_list, tb

valid_List, tbs = get_current_stocks()

# print(valid_List)
# history_test()