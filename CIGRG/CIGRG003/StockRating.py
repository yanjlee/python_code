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

import logging as log

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

######################################

start_date = '2017-01-01'
end_date = '2018-04-09'
request_date = '2018-04-12'

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

# 获取Stock列表，初始化列表dict，每股基础分100



# 基本面：获取ROE选择结果，每股加分？，权重？



# 技术面

## 三重滤网中板块和EMA选股，加减分，权重？


## 预测指标，每股加减分

## ATR和其他同步指标，每股加减分

## 滞后指标，各股加减分


# 分数排名，从高到低，取前10



