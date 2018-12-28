
# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import MONDAY, DateFormatter, DayLocator, WeekdayLocator

from mpl_finance import candlestick_ohlc


date1 = "2004-2-1"
date2 = "2004-4-12"


mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()              # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
dayFormatter = DateFormatter('%d')      # e.g., 12

quotes = pd.read_csv('D:/temp1/mpl_finance-master/examples/data/yahoofinance-INTC-19950101-20040412.csv',
                     index_col=0,
                     parse_dates=True,
                     infer_datetime_format=True)

# select desired range of dates
quotes = quotes[(quotes.index >= date1) & (quotes.index <= date2)]

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_minor_locator(alldays)
ax.xaxis.set_major_formatter(weekFormatter)
# ax.xaxis.set_minor_formatter(dayFormatter)

# plot_day_summary(ax, quotes, ticksize=3)
candlestick_ohlc(ax, zip(mdates.date2num(quotes.index.to_pydatetime()),
                         quotes['Open'], quotes['High'],
                         quotes['Low'], quotes['Close']),
                 width=0.6)

ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

# plt.show()

# conn, cur = connDB()
#
# items = 'symbol'
# tables = 'stk_fina_calc'
# condition = ' where date > \'2010-01-01\' group by symbol'
# data_info = get_all_data(items, tables, condition)
# symbol_list = []
# for i in data_info:
#     symbol_list.append(i[0])
#
# w.start()
#
# w_data = w.wsd(symbol_list, "roic_ttm", "2010-01-31", '2018-03-31', "Period=Q;Days=Alldays")
# for i in range(0,len(w_data.Codes)):
#     for j in range(0,len(w_data.Times)):
#         update_sql = 'update data.stk_fina_calc set roic_ttm = \'' + str(w_data.Data[i][j]) + '\' where symbol = \'' + w_data.Codes[i] + '\' and date = \'' + str(w_data.Times[j]) + '\''
#         try:
#             conn.cursor().execute(update_sql)
#         except Exception as e:
#             print(e)
#         conn.commit()
#     print(w_data.Codes[i] + ' is updated for ROIC')
#
# connClose(conn, cur)

# w.wsd("002456.SZ", "roic_ttm,roic_ttm2,roic,roic2_ttm,roic_ttm3", "2015-01-29", "2018-05-28", "Period=Q;Days=Alldays")