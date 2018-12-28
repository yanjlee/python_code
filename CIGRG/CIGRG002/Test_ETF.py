# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import urllib.request
from termcolor import colored, cprint
import re
from ConnectDB import connDB, connClose, get_data, get_all_data
from datetime import date, datetime, timedelta
import logging as log
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
########################################
pd_list = [5, 20, 22, 30]
start_date = '2017-01-01'
end_date = '2018-04-09'
TOP = 1
PERIOD = 3
PERCENT = 1
FEE_RATE = 0.0003
MONEY = 1000000
universe = (
    '159901.OF', '159902.OF', '159905.OF', '159915.OF', '159920.OF', '159938.OF', '159949.OF', '510050.OF', '510180.OF',
    '510230.OF', '510300.OF', '510500.OF', '510880.OF', '510900.OF', '511010.OF', '512660.OF', '512800.OF', '512880.OF',
    '512980.OF', '512990.OF', '513050.OF', '513100.OF', '518880.OF')

#######################################

# logger配置
BASE_DIR = os.path.dirname(__file__)
LOG_PATH = BASE_DIR + '/'
LOG_FILENAME = 'CIGRG_002_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'

# 创建一个logger
logger = log.getLogger('my_log')
logger.setLevel(log.DEBUG)

# 创建一个handler，用于写入日志文件
output_file = log.FileHandler(LOG_PATH + LOG_FILENAME)
output_file.setLevel(log.DEBUG)

# 再创建一个handler，用于输出到控制台
console_info = log.StreamHandler()
console_info.setLevel(log.DEBUG)

# 定义handler的输出格式
formatter = log.Formatter('[%(levelname)s] %(message)s')
output_file.setFormatter(formatter)
console_info.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(output_file)
logger.addHandler(console_info)
###################################

class MyAccount:
    def __init__(self):
        self.total_amount = {}
        self.cash = {}
        self.total_fee = {}
        self.stock_position = {}
        self.stock_price_holding = {}
        self.change_rate = {}
        self.cumulative_change_rate = {}

    def Show_Account(self, date):
        logger.info('********************')
        logger.info('date: ' + date)
        logger.info('total_amount: ' + str(self.total_amount[date]))
        logger.info('cash: ' + str(self.cash[date]))
        logger.info('total_fee: ' + str(self.total_fee[date]))
        logger.info('stock_position: ' + str(self.stock_position[date]))
        logger.info('stock_price_holding: ' + str(self.stock_price_holding[date]))
        logger.info('change_rate: ' + str(self.change_rate[date]))
        logger.info('cumulative_change_rate: ' + str(self.cumulative_change_rate[date]))


def get_etf_list(PERIOD):
    items = 'date, close'
    tables = 'idx_price'
    condition = ' where symbol = \'399300.SZ\' and  date between \'' + start_date + '\' and \'' + end_date + '\' order by date'
    price_info = get_all_data(items, tables, condition)
    idx_price = dict(price_info)
    df_price = pd.DataFrame(list(idx_price.values()), columns=['399300.SZ'], index=idx_price.keys())

    idx_down = df_price[:-1]
    idx_up = df_price[1:]
    idx_down.index = idx_up.index
    idx_chg = (idx_up - idx_down) * 100 / idx_down
    idx_chg = idx_chg[PERIOD-1:]

    for symbol in universe:
        items = 'date, close'
        tables = 'etf_price'
        condition = ' where symbol = \'' + symbol + '\' and  date between \'' + start_date + '\' and \'' + end_date + '\' order by date'
        price_info = get_all_data(items, tables, condition)
        temp_price = dict(price_info)
        temp_df = pd.DataFrame(list(temp_price.values()), columns=[symbol], index=temp_price.keys())
        df_price = df_price.merge(temp_df, how='left', left_index=True, right_index=True)

    df_down = df_price[:-PERIOD]
    df_up = df_price[PERIOD:]
    df_down.index = df_up.index
    date_list = list(df_up.index)
    df_chg = (df_up - df_down) * 100 / df_down
    # idx_chg = df_chg['399300.SZ']
    df_chg = df_chg.drop(columns=['399300.SZ'])

    # df_chg.iloc[0].sort_values(ascending=False)[0:3]
    raw_list = {}
    for date_k in df_chg.index:
        dict_temp = dict(df_chg.loc[date_k].sort_values(ascending=False)[0:TOP])
        raw_list[date_k.strftime('%Y-%m-%d')] = dict_temp

    etf_list = {}
    for i in raw_list:
        remove_list = []
        for j in raw_list[i]:
            if np.isnan(float(raw_list[i][j])) or raw_list[i][j] < PERCENT:
                remove_list.append(j)
        for k in remove_list:
            raw_list[i].pop(k)
        etf_list[i] = raw_list[i]

    return(etf_list, idx_chg, date_list)

################################################################

def start_account():
    # 建仓
    the_date = date_list[0].strftime('%Y-%m-%d')
    items = 'symbol, close'
    table = 'etf_price_backward'
    if len(etf_list[the_date]) != 0:
        db_data = get_data(items, table, list(etf_list[the_date].keys()), the_date, the_date)
        code_list = []
        stock_price = []
        for j in range(0, len(db_data)):
            code_list.append(db_data[j][0])
            stock_price.append(db_data[j][1])
        stock_position = {}
        stock_price_holding = {}
        for c in range(0, len(code_list)):
            stock_position[code_list[c]] = int(MONEY / len(code_list) / 100 / round(float(stock_price[c]), 3)) * 100
            stock_price_holding[code_list[c]] = round(float(stock_price[c]), 3)
        Account.stock_position[the_date] = stock_position
        Account.stock_price_holding[the_date] = stock_price_holding
        Account.total_fee[the_date] = round(sum([stock_price_holding[k] * stock_position[k] for k in stock_position]) * FEE_RATE, 2)
        Account.cash[the_date] = round(MONEY - sum([stock_price_holding[k] * stock_position[k] for k in stock_position]) * (1 + FEE_RATE), 2)
        Account.change_rate[the_date] = - Account.total_fee[the_date] * 100 / MONEY
        Account.cumulative_change_rate[the_date] = 1 + Account.change_rate[the_date] / 100
        Account.total_amount[the_date] = Account.cash[the_date] + round(sum([stock_price_holding[k] * stock_position[k] for k in stock_position]), 2)
    else: # 买入列表为空
        Account.stock_position[the_date] = {}
        Account.stock_price_holding[the_date] = {}
        Account.total_fee[the_date] = 0
        Account.cash[the_date] = MONEY
        Account.change_rate[the_date] = 0
        Account.cumulative_change_rate[the_date] = 1
        Account.total_amount[the_date] = MONEY
    Account.Show_Account(the_date)


def trade_account():
    # 按历史列表开始交易
    for d in range(1, len(date_list)):
        the_date = date_list[d].strftime('%Y-%m-%d')
        pre_date = date_list[d-1].strftime('%Y-%m-%d')
        pre_holding_list = list(etf_list[pre_date].keys())
        pre_holding_list.sort()
        current_list = list(etf_list[the_date].keys())
        current_list.sort()
        items = 'symbol, close'
        table = 'etf_price_backward'

        if pre_holding_list == current_list and len(pre_holding_list) != 0:
            db_data = get_data(items, table, current_list, the_date, the_date)
            code_list = []
            stock_price = []
            for j in range(0, len(db_data)):
                code_list.append(db_data[j][0])
                stock_price.append(db_data[j][1])
            stock_price_holding = {}
            for c in range(0, len(code_list)):
                stock_price_holding[code_list[c]] = round(float(stock_price[c]), 3)

            Account.stock_price_holding[the_date] = stock_price_holding
            Account.stock_position[the_date] = Account.stock_position[pre_date]
            Account.total_fee[the_date] = Account.total_fee[pre_date]
            Account.cash[the_date] = Account.cash[pre_date]
            Account.total_amount[the_date] = Account.cash[the_date] + round(
                sum([stock_price_holding[k] * Account.stock_position[pre_date][k] for k in Account.stock_position[pre_date]]), 2)
            Account.change_rate[the_date] = round(100 * (Account.total_amount[the_date]-Account.total_amount[pre_date])/Account.total_amount[pre_date], 3)
            Account.cumulative_change_rate[the_date] = round(Account.total_amount[the_date] / MONEY, 4)

        elif pre_holding_list == current_list and len(current_list) == 0:
            Account.stock_price_holding[the_date] = {}
            Account.stock_position[the_date] = {}
            Account.total_fee[the_date] = Account.total_fee[pre_date]
            Account.cash[the_date] = Account.total_amount[pre_date]
            Account.total_amount[the_date] = Account.total_amount[pre_date]
            Account.change_rate[the_date] = 0
            Account.cumulative_change_rate[the_date] = Account.cumulative_change_rate[pre_date]

        else:
            # sell_list = pre_holding_list
            buy_list = current_list

            total_trade_list = list(set(pre_holding_list + current_list))
            same_list = list(set(pre_holding_list).intersection(set(current_list)))
            diff_list = list(set(total_trade_list).difference(set(same_list)))
            db_data = get_data(items, table, total_trade_list, the_date, the_date)

            code_list = []
            stock_price = []
            for j in range(0, len(db_data)):
                code_list.append(db_data[j][0])
                stock_price.append(db_data[j][1])

            stock_position_sell = Account.stock_position[pre_date]
            stock_position_buy = {}
            stock_price_holding = {}
            all_price = {}
            for c in range(0, len(code_list)):
                all_price[code_list[c]] = round(float(stock_price[c]), 3)

            sell_currenct_cash = round(Account.cash[pre_date] + sum([all_price[k] * stock_position_sell[k] for k in stock_position_sell]), 2)

            for f in range(0, len(buy_list)):
                stock_position_buy[buy_list[f]] = int(sell_currenct_cash / len(buy_list) / 100 / all_price[buy_list[f]]) * 100
                stock_price_holding[buy_list[f]] = all_price[buy_list[f]]

            Account.stock_position[the_date] = stock_position_buy
            Account.stock_price_holding[the_date] = stock_price_holding

            Account.total_fee[the_date] = round(
                Account.total_fee[pre_date] + (Account.total_amount[pre_date] - Account.cash[pre_date]) * len(
                    diff_list) * FEE_RATE / (len(same_list) * 2 + len(diff_list)), 2)

            Account.cash[the_date] = round(sell_currenct_cash - sum(
                [stock_price_holding[k] * stock_position_buy[k] for k in stock_position_buy]) * (1 + FEE_RATE), 2)
            Account.total_amount[the_date] = round( Account.cash[the_date] + sum([stock_price_holding[k] * Account.stock_position[the_date][k] for k in Account.stock_position[the_date]]), 2)
            Account.change_rate[the_date] = round(
                100 * (Account.total_amount[the_date] - Account.total_amount[pre_date]) / Account.total_amount[
                    pre_date], 3)
            Account.cumulative_change_rate[the_date] = round(Account.total_amount[the_date] / MONEY, 4)


        Account.Show_Account(the_date)

def show_result():
    c_list = list(Account.change_rate.values())
    h_list = list(idx_chg['399300.SZ'])
    # chg_list = [c_list[i] - 0 * float(h_list[i]) for i in range(0, len(c_list))]
    chg_list = c_list

    # 指标计算
    hs300_cumulative = [1]
    cumulative_return_list = [1]
    for i in range(1, len(h_list)):
        hs300_cumulative.append(round(hs300_cumulative[i - 1] * (1 + h_list[i] / 100), 3))
        cumulative_return_list.append(round(cumulative_return_list[i - 1] * (1 + chg_list[i] / 100), 3))

    cumulative_return = round((cumulative_return_list[-1] - 1) * 100, 2)
    annualized_return = round((cumulative_return/100 + 1) ** (365.25/(datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days) -1, 4) * 100

    return_change_rate = np.array(list(Account.change_rate.values()))
    standard_deviation = np.std(return_change_rate, ddof=1) * ((365.25 * len(date_list)/(datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days)**0.5)
    sharp_ratio = round((annualized_return - 3) / standard_deviation, 2)

    max_draw_down = 0
    for j in range(0, len(cumulative_return_list)-1):
        for k in range(j+1, len(cumulative_return_list)):
            max_draw_down = min(max_draw_down, cumulative_return_list[k] / cumulative_return_list[j] - 1)
    max_draw_down = round(max_draw_down * 100, 2)
    pic_txt = '调仓间隔（天）：' + str(PERIOD) + '\n' +'总收益：' + str(cumulative_return) + '% 年化收益：' + str(round(annualized_return,2)) + '%' + ' 夏普率:' + str(sharp_ratio) + ' 最大回撤：' + str(max_draw_down) + '%\n' + '时间区间：' + start_date + ' ~ ' + end_date
    logger.info(pic_txt)

    # 做图
    x = np.array(date_list)
    y1 = np.array(cumulative_return_list)
    y2 = np.array(hs300_cumulative)
    plt.plot(x, y1, 'r', label='Cigrg_002')
    plt.plot(x, y2, 'b', label='HS300')
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('Date')
    plt.ylabel('Return')
    plt.legend(loc='upper left', frameon=False)
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=11)
    # plt.xticks(x, rotation=30)
    # font = {'family': 'SimHei', 'color': 'black', 'weight': 'normal', 'size': 11, }
    # plt.text(0.5, 0.5, pic_txt, fontdict=font)
    plt.title(pic_txt, loc ='left', fontproperties=font_set)
    plt.show()
    PNG_FILENAME = 'CIGRG_002_' + str(PERIOD) +'_' + str(datetime.now().strftime('%Y%m%d_%H%M%S') ) + '.png'
    plt.savefig(LOG_PATH + PNG_FILENAME)


####################################################
# for pd in pd_list:
#     etf_list, idx_chg, date_list = get_etf_list(pd)
etf_list, idx_chg, date_list = get_etf_list(PERIOD)
Account = MyAccount()
start_account()
trade_account()

