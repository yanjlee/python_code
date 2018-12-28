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

import logging as log

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

######################################

start_date = '2017-01-01'
end_date = '2018-04-12'


#####################################

items = 'date, close'
table = 'idx_price'
condition = ' where symbol=\'000905.SH\' and date between \'' + start_date + '\' and \'' + end_date + '\' order by date asc'
condition2 = ' where symbol=\'000016.SH\' and date between \'' + start_date + '\' and \'' + end_date + '\' order by date asc'
idx_price = dict(get_all_data(items, table, condition))
idx_price_2 = dict(get_all_data(items, table, condition2))
df_price = pd.DataFrame(list(idx_price.values()), columns=['IC500'], index=idx_price.keys())
df_price_2 = pd.DataFrame(list(idx_price_2.values()), columns=['IH50'], index=idx_price_2.keys())
temp_list = list(idx_price_2.values())
price_data_3 = [x*2.2 for x in temp_list]
df_price_3 = pd.DataFrame(price_data_3, columns=['IH50_adj'], index=idx_price_2.keys())
df = pd.concat([df_price, df_price_2,df_price_3], axis=1, join='inner')


