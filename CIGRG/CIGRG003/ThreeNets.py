# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=


from termcolor import colored, cprint
import re
from ConnectDB import connDB, connClose, get_data, get_all_data, fill_data
from datetime import date, datetime, timedelta
import logging as log
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import collections as clt
from dateutil.relativedelta import relativedelta

import logging as log

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

######################################

start_date = '2017-01-01'
end_date = '2018-04-09'
request_date = '2018-05-03'
# currentDate = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

######################################


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


conn, cur = connDB()

# 选出收盘价在20/60日均线之上的指数
req_sql = 'SELECT d.symbol, d.constk FROM (SELECT a.symbol FROM (SELECT symbol, date, close FROM data.idx_price WHERE date = \'' + request_date + '\') a INNER JOIN (SELECT symbol, date, ma20, ma60 FROM data.idx_price_tec WHERE date = \'' + request_date + '\') b ON a.symbol = b.symbol AND a.date = b.date WHERE a.close > b.ma20 AND a.close > b.ma60  GROUP BY a.symbol ORDER BY a.symbol) c INNER JOIN idx_info_constk d ON c.symbol = d.symbol WHERE d.name NOT LIKE \'%债%\' AND d.name NOT LIKE \'%信用%\' AND d.name NOT LIKE \'%次新%\' AND d.name NOT LIKE \'%深信%\''

try:
    cur.execute(req_sql)
    symbol_data = cur.fetchall()
except Exception as e:
    print(e)

## 获取指数成分股，按出现频率排序
symbol_data = dict(symbol_data)
symbols = ''
for i in symbol_data:
    symbols = symbols + ',' + str(symbol_data[i])

symbols = symbols.split(',')
symbol_count = clt.Counter(symbols)
symbol_count = sorted(symbol_count.items(), key=lambda symbol_count:symbol_count[1], reverse = True)
symbol_count = dict(symbol_count)
symbols = list(symbol_count.keys())

##  过滤掉出现次数小于6的股票
for i in symbols:
    if symbol_count[i] < 6:
        symbol_count.pop(i)

# 股票的当日 min(close, open) 站在21/55日ema线上, 且不在黑名单之列
ema_sql = 'select a.symbol from (select symbol, date, close, open from stk_price_forward where date = \'' + request_date + '\') a inner join (select symbol, date, ema21, ema55 from stk_price_tec where date =\'' + request_date + '\') b on a.symbol = b.symbol and a.date =b.date where a.close > b.ema21 and a.close > b.ema55 and a.open > b.ema21 and a.open > b.ema55 and a.symbol not in (select symbol from data.b_list) and a.symbol in ' + str(list(symbol_count.keys())).replace('[', '(').replace(']', ')')
try:
    cur.execute(ema_sql)
    db_data_ema = cur.fetchall()
except Exception as e:
    print(e)

symbol_ema = []
for i in db_data_ema:
    symbol_ema.append(i[0])

## 股票的当日 max(close, open) 站在5/10日ema线下, 被排除
ema_sql_2 = 'select a.symbol from (select symbol, date, close, open from stk_price_forward where date = \'' + request_date + '\') a inner join (select symbol, date, ema5, ema10 from stk_price_tec where date =\'' + request_date + '\') b on a.symbol = b.symbol and a.date =b.date where a.close < b.ema5 and a.close < b.ema10 and a.open < b.ema5 and a.open < b.ema10 and a.symbol in ' + str(symbol_ema).replace('[', '(').replace(']', ')')

try:
    cur.execute(ema_sql_2)
    db_data_ema_2 = cur.fetchall()
except Exception as e:
    print(e)

symbol_ema_remove = []
for i in db_data_ema_2:
    symbol_ema_remove.append(i[0])

symbol_ema = list(set(symbol_ema).difference(set(symbol_ema_remove)))

## 市盈利率筛选，范围[0, 80]
pe_sql = 'select symbol from data.stk_ratio where date =\'' + request_date + '\' and symbol in ' + str(symbol_ema).replace('[', '(').replace(']', ')') + ' and pe_ttm > 0 and pe_ttm < 61.8'
try:
    cur.execute(ema_sql)
    db_data_pe = cur.fetchall()
except Exception as e:
    print(e)

symbol_pe = []
for i in db_data_pe:
    symbol_pe.append(i[0])

## 过滤次新股，上市时间不足1年
ipo_sql = 'select symbol from data.stk_info where symbol in ' + str(symbol_pe).replace('[', '(').replace(']', ')') + ' and ipo < \'' + (datetime.strptime(request_date, '%Y-%m-%d') - relativedelta(years=1)).strftime('%Y-%m-%d')  + '\''

try:
    cur.execute(ipo_sql)
    db_data_ipo = cur.fetchall()
except Exception as e:
    print(e)

symbol_ipo = []
for i in db_data_ipo:
    symbol_ipo.append(i[0])

## 过滤东三省股票
area_sql = 'select symbol from data.stk_info where area not in (\'黑龙江\',\'吉林\',\'辽宁\') and symbol in ' + str(symbol_ipo).replace('[', '(').replace(']', ')')
try:
    cur.execute(area_sql)
    db_data_area = cur.fetchall()
except Exception as e:
    print(e)

symbol_area = []
for i in db_data_area:
    symbol_area.append(i[0])

## ATR止损过滤




connClose(conn, cur)