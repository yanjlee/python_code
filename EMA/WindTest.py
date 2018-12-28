
from WindPy import *
w.start()

w_data = w.wsd("600129.SH", "close", "2018-08-15", "2018-09-14", "Fill=Previous")
w_data_m = w.wsi("600016.SH", "open,high,low,close", "2018-09-14 09:00:00", "2018-09-14 18:42:53", "")