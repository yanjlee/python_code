
1# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from time import sleep
from CIGRG.WindPy import *
import prettytable as pt

#######################
symbol_list = ['000016.SH,IH1807.CFE,IH1808.CFE,IH1809.CFE,IH1812.CFE','000300.SH,IF1807.CFE,IF1808.CFE,IF1809.CFE,IF1812.CFE','000905.SH,IC1807.CFE,IC1808.CFE,IC1809.CFE,IC1812.CFE']
current_date = datetime.now()
Month1 = '2018-07-20'
Month2 = '2018-08-17'
Quarterly_Month = '2018-09-21'
Semi_annual_Month= '2018-12-21'
gap_1 = (datetime.strptime(Month1,'%Y-%m-%d') - current_date).days
gap_2 = (datetime.strptime(Month2,'%Y-%m-%d') - current_date).days
gap_3 = (datetime.strptime(Quarterly_Month,'%Y-%m-%d') - current_date).days
gap_4 = (datetime.strptime(Semi_annual_Month,'%Y-%m-%d') - current_date).days
#######################


w.start()

def show_table(rt_data):
    tb = pt.PrettyTable()
    tb.field_names = ['','Index', 'Month1', 'Month2', 'Quarterly_Month', 'Semi-annual_Month']
    for data in rt_data:
        tb.add_row(data)
    tb.align = 'l'
    # print(tb)
    return(tb)



def get_RT_price(symbol_list):
    rt_data = []
    for symbols in symbol_list:
        rt_percentage = []
        w_RT_price = w.wsq(symbols, "rt_latest",)
        rt_time = w_RT_price.Times[0].strftime('%Y-%m-%d %H:%M:%S')
        rt_codes = w_RT_price.Codes.copy()
        rt_codes.insert(0, 'Symbols')
        rt_price = w_RT_price.Data[0].copy()
        rt_price.insert(0, 'Price')
        rt_percentage = ['Percent', 0, "{:.3f}".format(100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][1])/w_RT_price.Data[0][0]), "{:.3f}".format(100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][2])/w_RT_price.Data[0][0]), "{:.3f}".format(100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][3])/w_RT_price.Data[0][0]), "{:.3f}".format(100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][4])/w_RT_price.Data[0][0]) ]
        if symbols.startswith('000905.SH'):
            rt_annualized = ['Annalized', 0, "{:.3f}".format(365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][1])/w_RT_price.Data[0][0]/gap_1/0.3), "{:.3f}".format(365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][2])/w_RT_price.Data[0][0]/gap_2/0.3), "{:.3f}".format(365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][3])/w_RT_price.Data[0][0]/gap_3/0.3), "{:.3f}".format(365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][4])/w_RT_price.Data[0][0]/gap_4/0.3) ]
        else:
            rt_annualized = ['Annalized', 0, "{:.3f}".format(
                365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][1]) / w_RT_price.Data[0][0] / gap_1/ 0.15),
                             "{:.3f}".format(
                                 365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][2]) / w_RT_price.Data[0][
                                     0] / gap_2 / 0.15), "{:.3f}".format(
                    365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][3]) / w_RT_price.Data[0][0] / gap_3 / 0.15),
                             "{:.3f}".format(
                                 365 * 100 * (w_RT_price.Data[0][0] - w_RT_price.Data[0][4]) / w_RT_price.Data[0][
                                     0] / gap_4 / 0.15)]
        rt_data.append(rt_codes)
        rt_data.append(rt_price)
        rt_data.append(rt_percentage)
        rt_data.append(rt_annualized)
    return(rt_time, rt_data)


def trade_loop():
    pre_signal = 0
    while True:
        now_time = datetime.now()
        if '09:30:00' <= now_time.strftime('%H:%M:%S') < '11:30:00' or '13:00:00' <= now_time.strftime('%H:%M:%S') < '15:00:00':
            rt_time, rt_data = get_RT_price(symbol_list)
            tb = show_table(rt_data)
            print(rt_time)
            print(tb)
            sleep(15)
        elif now_time.strftime('%H:%M:%S') > '11:30:00' and now_time.strftime('%H:%M:%S') < '12:59:00':
            print('Midday, breaking sleep: ' + now_time.strftime('%H:%M:%S'))
            sleep(60)
        elif now_time.strftime('%H:%M:%S') > '15:03:00':
            print('Market is closed today.')
            break
        else:
            now_time = now_time + timedelta(seconds=5)
            print('Not trading time: ' + now_time.strftime('%H:%M:%S'))
            sleep(5)


trade_loop()