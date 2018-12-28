import pandas as pd
import numpy as np
# from fbprophet import Prophet
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from ConnectDB import get_all_data


# %matplotlib inline

plt.rcParams['figure.figsize']=(20,10)
plt.style.use('ggplot')

items = 'date,close'
table = ' idx_price'
condition = 'where symbol = \'000300.SH\' and date >= \'2017-01-05\' and date <= \'2018-09-09\'  order by date asc'
symbol_data = get_all_data(items, table, condition)
df = pd.DataFrame(list(symbol_data), columns=['ds', 'y'])
df['y'] = df['y'].astype('float64')
# # market_df = pd.read_csv('../examples/SP500.csv', index_col='DATE', parse_dates=True)
df['y'] = np.log(df['y'])

#lets take a look at our data quickly
df.set_index('ds').y.plot()