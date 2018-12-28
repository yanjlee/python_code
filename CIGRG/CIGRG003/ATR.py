# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from termcolor import colored, cprint
import re
from ConnectDB import connDB, connClose, get_data, get_all_data
from datetime import date, datetime, timedelta
import logging as log
import numpy as np
import pandas as pd
import talib
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import logging as log

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

######################################

start_date = '2017-01-01'
end_date = '2018-04-09'
TOP = 1
PERIOD = 3
PERCENT = 1
FEE_RATE = 0.0003
MONEY = 1000000

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

