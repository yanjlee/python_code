from datetime import datetime, timedelta
import pandas as pd
from ConnectDB import get_all_data
import math
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import numpy as np
import talib as ta
from WindPy import w

w.start()

start_date = '2018-12-10 14:29:00'
end_date = '2018-12-12 15:00:01'


i = '000002.SZ'
# w_data = w.wsi(i, "open,high,low,close", start_date, end_date,"unit=1;currencyType=")
pf = open('C:\\codes\\NEW\\pywsqdataif.data', 'w')

def myCallback(indata):
    if indata.ErrorCode!=0:
        print('error code:'+str(indata.ErrorCode)+'\n');
        return();

    global begintime
    lastvalue ="";
    for k in range(0,len(indata.Fields)):
         if(indata.Fields[k] == "RT_TIME"):
            begintime = indata.Data[k][0];
         if(indata.Fields[k] == "RT_LAST"):
            lastvalue = str(indata.Data[k][0]);

    string = str(begintime) + " " + lastvalue +"\n";
    pf.writelines(string)
    print(string);

w.wsq("600000.SH","rt_low,rt_last_vol",func=myCallback)


