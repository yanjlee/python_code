# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from works.StockBox import get_stock_list, valid_list
from ConnectDB import get_all_data
import pandas as pd

########################
## 初始设定
hold_days = 5
period_days = 40
top_list = 10
s_date = '2018-01-01'
e_date = '2018-07-10'
#########################

# 获取基本数据
items = 'date'
table = 'idx_price'
condition = ' where symbol =\'000001.SH\' and date >= \''+ s_date +'\' and date <= \''+ e_date +'\' order by date asc'
idx_data = get_all_data(items, table, condition)
date_list =[]
for i in idx_data:
    date_list.append(i[0].strftime('%Y-%m-%d'))


down_list = []
for dt in date_list:
    items = 'date'
    table = 'idx_price'
    condition = ' where symbol =\'000001.SH\' and date < \'' + dt + '\' order by date desc limit ' + str(period_days)
    idx_data_2 = get_all_data(items, table, condition)

    current_date = idx_data_2[0][0].strftime('%Y-%m-%d')
    start_date = idx_data_2[-1][0].strftime('%Y-%m-%d')
    symbol_list = get_stock_list(current_date)

# 生成symbol库
    code_list = list(set(valid_list).intersection(set(symbol_list)))
    items = 'a.symbol, a.close as s_close, b.close as e_close'
    table = 'stk_price_forward a inner join data.stk_price_forward b on a.symbol=b.symbol and a.date = \'' + start_date + '\' and b.date = \'' + current_date + '\''
    condition = ' where a.symbol in (' + str(code_list).replace('[','').replace(']','') + ')'
    stk_data = get_all_data(items, table, condition)
#
# # 计算下跌率，取最后的多少位

    stk_chg = pd.DataFrame(list(stk_data),columns = ['symbol','s_close','e_close'])
    stk_chg['chg'] = 100 * (stk_chg['e_close'] - stk_chg['s_close']) / stk_chg['s_close'] # 计算下跌率
    down_list.append(list(stk_chg.sort_values('chg')['symbol'][0:top_list])) # 选出下跌最大的前Top_list位

# 计算持有回报
hold_return = {}
cl_return = [1]
for k in range(0, len(down_list), hold_days):
    date_gaps = date_list[k:k+hold_days]
    return_list = []
    for j in down_list[k]:
        items = 'chgrate'
        table = 'stk_price'
        condition = ' where symbol =\'' + j + '\' and date in (' + str(date_gaps).replace('[','').replace(']','') + ') order by date asc'
        chg_data = get_all_data(items, table, condition)
        cumulative_return = 1
        for i in chg_data:
            cumulative_return = cumulative_return * (1 + i[0]/100 )
        return_list.append(100*(cumulative_return-1))
    rt_temp = round(float(sum(return_list) / len(down_list[k])),3)
    hold_return[date_list[k]] = rt_temp
    cl_return.append(round(cl_return[-1] * (1 + rt_temp/100),3))

print(cl_return)

    # print(current_date + ': '+ str(down_list))
    # print(down_list)