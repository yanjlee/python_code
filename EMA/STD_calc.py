# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=


from datetime import datetime, timedelta
from works.StockBox import get_stock_list
import pandas as pd
from ConnectDB import get_all_data
from decimal import Decimal
import numpy as np


current_date = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d')
pre_years_date= (datetime.now() + timedelta(days=-365)).strftime('%Y-%m-%d')
# current_date = '2018-06-29'
stock_list = get_stock_list(current_date)
# stock_list = ['002456.SZ']

stk_std = {}
for i in stock_list:
    items = 'open, close'
    table = 'stk_price_forward'
    condition = 'where symbol = \'' + i + '\' and date >= \'' + pre_years_date + '\' order by date asc'
    symbol_data = get_all_data(items, table, condition)

    stk_data = pd.DataFrame(list(symbol_data),columns = ['open','close'])

    stk_data['return'] =  100 * (stk_data['close'] - stk_data['open']) / stk_data['open']
    stk_data['return'] = stk_data['return'].astype(float)
    std_value = stk_data['return'].std()
    stk_std[i] = round(std_value,3)