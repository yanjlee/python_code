# -*- coding: utf-8 -*-
"""
@author: GuoJun
"""
from StockPool import stock_list
from HoldingList import Holding
from ConnectDB import connDB, connClose, get_data
import logging as log
import numpy as np
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
import os
import time
from matplotlib.font_manager import FontProperties

#############################
# 常量设置
startDate = '2015-01-03'
endDate = '2015-12-31'
# endDate = (datetime.now()-timedelta(1)).strftime('%Y-%m-%d')
# PERIOD - 调仓频率，FEE - 交易手续费率，MONEY- 账户初始资金，STOP/STOP_ON 止损项设置，OPPOSITE对冲百分比
PERIOD = 1
FEE_RATE = 0.0003
TAX_RATE = 0.001
MONEY = 1000000
STOP = 3
STOP_ON = 1
OPPOSTIE = 0
###################

# logger配置
BASE_DIR = os.path.dirname(__file__)
LOG_PATH = BASE_DIR + '/'
LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))) + '.log'

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

# logger.info('Testing start...')

# 创建账户类
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


def get_hs300():# 获取沪深300（399300.SZ）或上证50（000016.SH）交易日期和涨跌幅作为基准参考

    query_sql = 'select date, chgrate from data.idx_price where symbol = \'399300.SZ\' and date between \'' + startDate + '\' and \'' + endDate + '\' order by date'
    try:
        cur.execute(query_sql)
        hs300_data = cur.fetchall()
    except Exception as e:
        print(e)
    trade_date = []
    hs300_chgrate = []
    for g in range(0, len(hs300_data)):
        trade_date.append(hs300_data[g][0])
        hs300_chgrate.append(hs300_data[g][1])

    return(trade_date, hs300_chgrate)

def get_cfe():
    cfe_symbol = 'I1806.CFE'
    query_sql = 'select datetime, open from data.fur_price where symbol =\'' + cfe_symbol + '\' and datetime like \'%09:30:00\' and datetime between \'' + trade_date[0].strftime('%Y-%m-%d') + ' 09:30:00\' and \'' + trade_date[-1].strftime('%Y-%m-%d') + ' 14:59:00\' order by datetime asc'
    try:
        cur.execute(query_sql)
        cfe_open = cur.fetchall()
    except Exception as e:
        print(e)

    query_sql_2 = 'select datetime, close from data.fur_price where symbol =\'' + cfe_symbol + '\' and datetime like \'%14:59:00\' and datetime between \'' + trade_date[0].strftime('%Y-%m-%d') + ' 09:30:00\' and \'' + trade_date[-1].strftime('%Y-%m-%d') + ' 14:59:00\' order by datetime asc'
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

    chg_rate_cfe = []
    for k in open_data:
        temp_chg = (close_data[k] - open_data[k]) / close_data[k] * 100
        chg_rate_cfe.append(temp_chg)

    return(chg_rate_cfe)

def get_holding_list(trade_date):
    # 获取调仓日股票持仓列表
    period_date = []
    set_list = []
    holding_list = {}
    for i in range(0, len(trade_date), PERIOD):
        period_date.append(trade_date[i].strftime('%Y-%m-%d'))
        stk_list, all_list = stock_list(trade_date[i].strftime('%Y-%m-%d'))
        set_list.append(stk_list)
        logger.info(period_date[-1])
        logger.info(stk_list)
    for a in range(0, len(period_date)):
        holding_list[period_date[a]] = set_list[a]
    return (holding_list)


def fill_holding_list(): # 其他交易日，填充调仓日的持仓股票，以便后期止损对dict内容调整
    for b in range(1, len(trade_date)):
        if trade_date[b].strftime('%Y-%m-%d') in holding_list.keys():
            pass
        else:
            holding_list[trade_date[b].strftime('%Y-%m-%d')] = holding_list[trade_date[b-1].strftime('%Y-%m-%d')]
    return (holding_list)


def start_account():
    # 建仓
    the_date = trade_date[0].strftime('%Y-%m-%d')
    items = 'symbol, close'
    table = 'stk_price_forward'
    if len(holding_list[the_date]) != 0:
        db_data = get_data(items, table, holding_list[the_date], the_date, the_date)
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

def stop_loss(the_date):
    adj_date = []
    for i in range(0, len(trade_date), PERIOD):
        adj_date.append(trade_date[i].strftime('%Y-%m-%d'))
    # 账户总额下跌超过3%，清仓至下一个调整日
    if Account.change_rate[the_date] < -STOP:
        pre_cl_date = the_date
        for j in range(0, len(adj_date)):
            if pre_cl_date < adj_date[j]:
                after_cl_date = adj_date[j]
                break
        cl_date = trade_date[trade_date.index(datetime.date(datetime.strptime(pre_cl_date,'%Y-%m-%d'))):trade_date.index(datetime.date(datetime.strptime(after_cl_date,'%Y-%m-%d')))]
        for k in range(1, min(1+STOP, len(cl_date))):
            holding_list[cl_date[k].strftime('%Y-%m-%d')] = []


def trade_account():
    # 按历史列表开始交易
    for d in range(1, len(trade_date)):
        the_date = trade_date[d].strftime('%Y-%m-%d')
        pre_date = trade_date[d-1].strftime('%Y-%m-%d')
        pre_holding_list = holding_list[pre_date]
        pre_holding_list.sort()
        holding_list[the_date].sort()
        items = 'symbol, close'
        table = 'stk_price_forward'

        if pre_holding_list == holding_list[the_date] and len(pre_holding_list) != 0:
            # stock_price = w.wsd(holding_list[the_date], "close", the_date, the_date, "Fill=Previous;PriceAdj=F")
            db_data = get_data(items, table, holding_list[the_date], the_date, the_date)
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

        elif pre_holding_list == holding_list[the_date] and len(holding_list[the_date]) == 0:
            Account.stock_price_holding[the_date] = {}
            Account.stock_position[the_date] = {}
            Account.total_fee[the_date] = Account.total_fee[pre_date]
            Account.cash[the_date] = Account.total_amount[pre_date]
            Account.total_amount[the_date] = Account.total_amount[pre_date]
            Account.change_rate[the_date] = 0
            Account.cumulative_change_rate[the_date] = Account.cumulative_change_rate[pre_date]

        elif set(holding_list[the_date]) > set(pre_holding_list):
            buy_list = list(set(holding_list[the_date]).difference(set(pre_holding_list)))
            db_data = get_data(items, table, holding_list[the_date], the_date, the_date)
            code_list = []
            stock_price = []
            for j in range(0, len(db_data)):
                code_list.append(db_data[j][0])
                stock_price.append(db_data[j][1])
            stock_position = {}
            stock_price_holding = {}
            for c in range(0, len(code_list)):
                stock_price_holding[code_list[c]] = round(float(stock_price[c]), 3)
            for e in range(0, len(buy_list)):
                stock_position[buy_list[e]] = int(Account.cash[pre_date] / len(buy_list) / 100 / round(stock_price_holding[buy_list[e]], 3)) * 100

            Account.stock_price_holding[the_date] = stock_price_holding.copy()
            Account.stock_position[the_date] = dict(stock_position, **Account.stock_position[pre_date])
            Account.total_fee[the_date] = Account.total_fee[pre_date] + round(
                sum([stock_price_holding[k] * stock_position[k] for k in stock_position]) * FEE_RATE, 2)
            Account.cash[the_date] = round(Account.cash[pre_date] - sum(
                [stock_price_holding[k] * stock_position[k] for k in stock_position])*(1 + FEE_RATE), 2)
            Account.total_amount[the_date] = Account.cash[the_date] + round(
                sum([stock_price_holding[k] * Account.stock_position[the_date][k] for k in Account.stock_position[the_date]]), 2)
            Account.change_rate[the_date] = round(100 * (Account.total_amount[the_date]-Account.total_amount[pre_date])/Account.total_amount[pre_date], 3)
            Account.cumulative_change_rate[the_date] = round(Account.total_amount[the_date] / MONEY, 4)

        elif set(pre_holding_list) > set(holding_list[the_date]):
            sell_list = list(set(pre_holding_list).difference(set(holding_list[the_date])))
            db_data = get_data(items, table, pre_holding_list, the_date, the_date)
            code_list = []
            stock_price = []
            for j in range(0, len(db_data)):
                code_list.append(db_data[j][0])
                stock_price.append(db_data[j][1])

            stock_position = {}
            stock_price_holding = {}
            for c in range(0, len(code_list)):
                stock_price_holding[code_list[c]] = round(float(stock_price[c]), 3)
            Account.stock_price_holding[the_date] = stock_price_holding.copy()
            Account.stock_position[the_date] = Account.stock_position[pre_date]
            for e in range(0, len(sell_list)):
                stock_position[sell_list[e]] = Account.stock_position[pre_date][sell_list[e]]
                Account.stock_price_holding[the_date].pop(sell_list[e])
                Account.stock_position[the_date].pop(sell_list[e])

            Account.total_fee[the_date] = Account.total_fee[pre_date] + round(
                sum([stock_price_holding[k] * stock_position[k] for k in stock_position]) * (FEE_RATE + TAX_RATE), 2)
            Account.cash[the_date] = round(Account.cash[pre_date] + sum(
                [stock_price_holding[k] * stock_position[k] for k in stock_position]) * (1 - FEE_RATE - TAX_RATE), 2)
            Account.total_amount[the_date] = Account.cash[the_date] + round(
                sum([stock_price_holding[k] * Account.stock_position[the_date][k] for k in
                     Account.stock_position[the_date]]), 2)
            Account.change_rate[the_date] = round(
                100 * (Account.total_amount[the_date] - Account.total_amount[pre_date]) / Account.total_amount[
                    pre_date], 3)
            Account.cumulative_change_rate[the_date] = round(Account.total_amount[the_date] / MONEY, 4)

        else:
            sell_list = list(set(pre_holding_list).difference(set(holding_list[the_date])))
            buy_list = list(set(holding_list[the_date]).difference(set(pre_holding_list)))
            total_trade_list = list(set(pre_holding_list + holding_list[the_date]))
            db_data = get_data(items, table, total_trade_list, the_date, the_date)
            code_list = []
            stock_price = []
            for j in range(0, len(db_data)):
                code_list.append(db_data[j][0])
                stock_price.append(db_data[j][1])
            stock_position_sell = {}
            stock_position_buy = {}
            stock_price_holding = {}
            for c in range(0, len(code_list)):
                stock_price_holding[code_list[c]] = round(float(stock_price[c]), 3)

            Account.stock_price_holding[the_date] = stock_price_holding.copy()
            Account.stock_position[the_date] = Account.stock_position[pre_date]
            for e in range(0, len(sell_list)):
                stock_position_sell[sell_list[e]] = Account.stock_position[pre_date][sell_list[e]]
                Account.stock_price_holding[the_date].pop(sell_list[e])
                Account.stock_position[the_date].pop(sell_list[e])

            currenct_cash = Account.cash[pre_date] + round(
                sum([stock_price_holding[k] * stock_position_sell[k] for k in stock_position_sell]) * (1 - FEE_RATE - TAX_RATE), 2)
            for f in range(0, len(buy_list)):
                stock_position_buy[buy_list[f]] = int(currenct_cash / len(buy_list) / 100 / round(stock_price_holding[buy_list[f]], 3)) * 100

            Account.stock_position[the_date] = dict(stock_position_buy, **Account.stock_position[the_date])
            Account.total_fee[the_date] = round(Account.total_fee[pre_date] +
                sum([stock_price_holding[k] * stock_position_sell[k] for k in stock_position_sell]) * (FEE_RATE + TAX_RATE) +
                sum([stock_price_holding[k] * stock_position_buy[k] for k in stock_position_buy]) * FEE_RATE, 2)

            Account.cash[the_date] = round(currenct_cash - sum(
                [stock_price_holding[k] * stock_position_buy[k] for k in stock_position_buy]) * (1 + FEE_RATE), 2)
            Account.total_amount[the_date] = Account.cash[the_date] + round(
                sum([stock_price_holding[k] * Account.stock_position[the_date][k] for k in
                     Account.stock_position[the_date]]), 2)
            Account.change_rate[the_date] = round(
                100 * (Account.total_amount[the_date] - Account.total_amount[pre_date]) / Account.total_amount[
                    pre_date], 3)
            Account.cumulative_change_rate[the_date] = round(Account.total_amount[the_date] / MONEY, 4)

        if STOP_ON == 1:
            stop_loss(the_date)
        Account.Show_Account(the_date)

if STOP_ON == 1:
    print('Stop Loss is ON.')
else:
    print('No Stop Loss conditions.')

# 作图和指标计算
def show_result(chg_rate):
    c_list = list(Account.change_rate.values())
    h_list = chg_rate
    chg_list = [c_list[i] - OPPOSTIE * float(h_list[i]) for i in range(0, len(c_list))] # 使用沪深300或上证50空单期货收益对冲

    # 指标计算
    hs300_cumulative = [1]
    cumulative_return_list = [1]
    for i in range(1, len(hs300_chgrate)):
        hs300_cumulative.append(round(hs300_cumulative[i - 1] * (1 + hs300_chgrate[i] / 100), 3))
        cumulative_return_list.append(round(cumulative_return_list[i - 1] * (1 + chg_list[i] / 100), 3))

    cumulative_return = round((cumulative_return_list[-1] - 1) * 100, 2)
    annualized_return = round((cumulative_return/100 + 1) ** (365.25/(datetime.strptime(endDate, '%Y-%m-%d') - datetime.strptime(startDate, '%Y-%m-%d')).days) -1, 4) * 100

    return_change_rate = np.array(list(Account.change_rate.values()))
    standard_deviation = np.std(return_change_rate, ddof=1) * ((365.25 * len(trade_date)/(datetime.strptime(endDate, '%Y-%m-%d') - datetime.strptime(startDate, '%Y-%m-%d')).days)**0.5)
    sharp_ratio = round((annualized_return - 3) / standard_deviation, 2)

    max_draw_down = 0
    for j in range(0, len(cumulative_return_list)-1):
        for k in range(j+1, len(cumulative_return_list)):
            max_draw_down = min(max_draw_down, cumulative_return_list[k] / cumulative_return_list[j] - 1)
    max_draw_down = round(max_draw_down * 100, 2)
    pic_txt = '调仓间隔（天）：' + str(PERIOD) + '\n' +'总收益：' + str(cumulative_return) + '% 年化收益：' + str(round(annualized_return,2)) + '%' + ' 夏普率:' + str(sharp_ratio) + ' 最大回撤：' + str(max_draw_down) + '%\n' + '时间区间：' + startDate + ' ~ ' + endDate
    logger.info(pic_txt)

    # 做图
    x = np.array(trade_date)
    y1 = np.array(cumulative_return_list)
    y2 = np.array(hs300_cumulative)
    plt.plot(x, y1, 'r', label='Cigrg_001')
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
    # plt.show()
    PNG_FILENAME = 'CIGRG_001_' + str(PERIOD) +'_' + str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))) + '.png'
    plt.savefig(LOG_PATH + PNG_FILENAME)

######################################
conn, cur = connDB()
trade_date, hs300_chgrate = get_hs300()

# chg_rate_cfe = get_cfe()
holding_list = get_holding_list(trade_date)
for hl in holding_list:
    logger.info(hl)

# holding_list = Holding(trade_date, PERIOD)
holding_list = fill_holding_list()
Account = MyAccount()
start_account()
trade_account()
show_result(hs300_chgrate)
# show_result(chg_rate_cfe)

connClose(conn, cur)
