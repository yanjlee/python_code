# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import datetime
import pandas as pd
import numpy as np
from ConnectDB import connDB, connClose, get_all_data, get_data


def winsorize(se):
    q = se.quantile([0.025, 0.975])
    p = []
    if isinstance(q, pd.Series) and len(q) == 2:
        # se[se < q.iloc[0]] = q.iloc[0]
        # se[se > q.iloc[1]] = q.iloc[1]
        for i in range(0, len(se)):
            if se.iloc[i] < q.iloc[0]:
                p.append(q.iloc[0])
            elif se.iloc[i] > q.iloc[1]:
                p.append(q.iloc[1])
            else:
                p.append(se.iloc[i])
    p = pd.DataFrame(p)
    return p


def standardize(se):
    se_std = se.std()
    se_mean = se.mean()
    return (se - se_mean) / se_std

# 获取计算数据
items = 'symbol, pe_ttm'
table = 'stk_ratio'
condition = ' where  date =\'2018-05-03\' order by symbol limit 100'
stk_data = get_all_data(items, table, condition)
temp = []
for i in list(stk_data):
    temp.append([i[0],float(i[1])])
pe_data = pd.DataFrame(temp, columns=['symbol','PE'])

# 去极值化
pe_data['winsorize'] = winsorize(pe_data['PE'])
# pe_data[['PE','winsorize']].plot()

# 标准化
pe_data['Zscore'] = standardize(pe_data['winsorize'])

# 行业中性化