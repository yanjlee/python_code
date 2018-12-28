from CIGRG.WindPy import *
import pandas as pd
import matplotlib.pylab as plt

w.start()

dat = w.wsd("002456.SZ", "open,high,low,close,volume,amt", "2017-12-17",
            "2018-03-06", "TradingCalendar=SZSE;Fill=Previous")

fm = pd.DataFrame(dat.Data, index=dat.Fields, columns=dat.Times)  # pandas timeseries type
fm = fm.T

type(fm['OPEN'])

fm['CLOSE'].plot(color='red')
plt.show()
