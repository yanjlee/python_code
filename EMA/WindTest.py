from WindPy import *
w.start()

symbol = '127008.SZ'
start = '219-05-19'
end = '2019-05-21'

w_data = w.wsd(symbol, "close", start, end, "Fill=Previous")
w_data_m = w.wsi(symbol, "open,high,low,close", start,end, "")
print(w_data)
print(w_data_m)