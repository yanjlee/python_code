# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from datetime import timedelta, datetime
from ConnectDB import get_all_data
import pandas as pd

startdate = (datetime.now() - timedelta(365 * 5)).strftime('%Y-%m-%d')
enddate = (datetime.now()).strftime('%Y-%m-%d')

items = 'date, close'
table = 'stk_price_forward'
condition = ' where symbol = \'002456.SZ\' and date between \'' + startdate + '\' and \'' + enddate + '\'order by date asc'
stk_data = get_all_data(items, table, condition)

stk_temp = {}
for i in stk_data:
    stk_temp[i[0]] =float(i[1])
stk_price = pd.DataFrame(list(stk_temp.values()), index=stk_temp.keys(), columns=['close'])
stk_price['std'] = stk_price.rolling(window=252,center=False).std()
stk_price['sha'] = stk_price['close'] /stk_price['std']
stk_price.plot()

# winddata = w.wsd("510050.SH", "close", startdate, enddate, "Fill=Previous")
# etf = pd.DataFrame(winddata.Data[0], index=winddata.Times, columns=['50ETF'])
# etf['std_252'] = pd.rolling_std(etf, 252)  # 计算252个交易日的标准差
# etf = etf.dropna(axis=0, how='any')
# etf['std_252'].plot()

