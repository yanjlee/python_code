1# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import logging as log
import os
from time import sleep
from CIGRG.WindPy import *
import prettytable as pt

#######################
Symbol = 'rb1810.SHF'
gap = 1
unit =1
close_list = []
#######################


w.start()

# logger配置
BASE_DIR = os.path.dirname(__file__)
LOG_PATH = BASE_DIR + '/logs/'
LOG_FILENAME = 'CIGRG_005_' + datetime.now().strftime('%Y%m%d') + '.log'
LOG_FILE = LOG_PATH + LOG_FILENAME

# 创建一个logger
logger = log.getLogger('my_log')
logger.setLevel(log.DEBUG)

# 创建一个handler，用于写入日志文件
output_file = log.FileHandler(LOG_PATH + LOG_FILENAME)
output_file.setLevel(log.DEBUG)

# 再创建一个handler，用于输出到控制台
console_info = log.StreamHandler()
console_info.setLevel(log.DEBUG)

# 定义handler的输出格式
formatter = log.Formatter('[%(levelname)s] %(message)s')
output_file.setFormatter(formatter)
console_info.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(output_file)
logger.addHandler(console_info)

# logger.info('Testing start...')

# # 创建账户类
# class MyAccount:
#     def __init__(self):
#         self.datetime = {}
#         self.total_amount = {}
#         self.cash = {}
#         self.total_fee = {}
#         self.stock_position = {}
#         self.trade_side = {}
#         self.change_rate = {}
#         self.cumulative_change_rate = {}
#
#     def Show_Account(self, date):
#         logger.info('********************')
#         logger.info('datetime: ' + datetime)
#         logger.info('total_amount: ' + str(self.total_amount[date]))
#         logger.info('cash: ' + str(self.cash[date]))
#         logger.info('total_fee: ' + str(self.total_fee[date]))
#         logger.info('stock_position: ' + str(self.stock_position[date]))
#         logger.info('stock_price_holding: ' + str(self.stock_price_holding[date]))
#         logger.info('change_rate: ' + str(self.change_rate[date]))
#         logger.info('cumulative_change_rate: ' + str(self.cumulative_change_rate[date]))


def Show(querty_data):
    tb = pt.PrettyTable()
    tb.field_names = querty_data.Fields
    temp = []
    for i in querty_data.Data:
        temp.append(i[0])
    tb.add_row(temp)
    tb.align = 'l'
    print(tb)
    return(tb)


def trade_init():
    with open(LOG_FILE, 'a') as file_log:
        start_message = '******Initialize trading on ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(start_message)
        file_log.write(start_message)

        # Login = w.tlogon('0000', '0', 'W3184800401', 'g66196619', 'SHSZ')
        ## 登陆
        Login = w.tlogon('0000', '0', 'W3184800402', 'g66196619', 'SHF')
        file_log.write(str(Show(Login)))
        w_query = w.tquery(0) # 查询账户基本信息
        file_log.write(str(Show(w_query)))


    # return account, trade_price


def get_RT_price():
    w_RT_price = w.wsq(Symbol, "rt_time,rt_date,rt_latest")
    RT_price = [w_RT_price.Times[0].strftime('%Y-%m-%d %H:%M:%S'), w_RT_price.Data[2][0]]
    return RT_price


def RT_trade(RT_price):
    global close_list
    close_list.append(RT_price[1])
    if len(close_list) > 55:
        del close_list[0]
    elif len(close_list) == 1:
        close_list = close_list * 55

    ace = round(0.382 * close_list[-2] + 0.618 * close_list[-1], 2)

    ema_list = [5,21,55]
    ema_values = []
    for i in ema_list:
        deno = (1 + i) * i / 2
        nume = 0
        for n in range(0, i):
            nume = round((i - n) * close_list[-n - 1] / deno + nume, 3)
        ema_values.append(nume)

    ema5 = ema_values[0]
    ema21 = ema_values[1]
    ema55 = ema_values[2]

# # ace & ema5 简单判断
#     if ace > ema5:
#         signal = -1
#     elif ace == ema5:
#         signal = 0
#     elif ace < ema5:
#         signal = 1
#     else:
#         signal = 0

## ace, ema5, ema21 & ema55 综合判断，长进短出
    if min(close_list[-1], close_list[-2]) > max(ema21, ema55):
        if ace > ema5:
            signal = 1
        else:
            signal = 0
    elif max(close_list[-1], close_list[-2]) < min(ema21, ema55):
        if ace < ema5:
            signal = -1
        else:
            signal = 0
    else:
        signal = 0


    if datetime.now().strftime('%H:%M:%S') > '22:55:00' or datetime.now().strftime('%H:%M:%S') < '09:01:00':
        signal = 0

    RT_price.extend([ace, ema5, signal])
    return RT_price


def go_trade(pre_signals,signals,close):
    signal = signals
    pre_signal = pre_signals
    Login = w.tquery('LogonID')
    global LogonId
    LogonId = Login.Data[0][0]
    w_status = w.tquery('Position', 'logonid=' + str(LogonId) + ',Windcode=' + Symbol + '\'')
    w_info = {}
    for i in range(0, len(w_status.Fields)):
        w_info[w_status.Fields[i]] = w_status.Data[i][0]

    # orders_status = w.tquery('Order', 'logonID=' + str(LogonId) + '\'')
    if signal == 1 and pre_signal == 1:# and orders_status.Data[1][-1] == 'Normal':
        if len(w_status.Fields) == 3 or w_info['SecurityCode'] == None:
            ord = w.torder(Symbol, 'Buy', close + gap, unit, 'OrderType=LMT,logonid=' + str(LogonId) + '\'')
            print(ord)
        elif w_info['SecurityCode'] == Symbol and w_info['TradeSide'] == 'Short':
            ord = w.torder(Symbol, 'CoverToday', close + gap, unit, 'OrderType=BOC,logonid=' + str(LogonId) + '\'')
            ord2 = w.torder(Symbol, 'Buy', close + gap, unit, 'OrderType=LMT,logonid=' + str(LogonId) + '\'')
            print(ord)
            print(ord2)
    elif signal == -1 and pre_signal == -1:#and orders_status.Data[1][-1] == 'Normal':
        if len(w_status.Fields) == 3 or w_info['SecurityCode'] == None:
            ord3 = w.torder(Symbol, 'Short', close - gap, unit, 'OrderType=LMT,logonid=' + str(LogonId) + '\'')
            print(ord3)
        elif w_info['SecurityCode'] == Symbol and w_info['TradeSide'] == 'Buy':
            ord4 = w.torder(Symbol, 'SellToday', close - gap, unit, 'OrderType=BOC,logonid=' + str(LogonId) + '\'')
            ord5 = w.torder(Symbol, 'Short', close - gap, unit, 'OrderType=LMT,logonid=' + str(LogonId) + '\'')
            print(ord4)
            print(ord5)

    elif signal == 0 and pre_signal == 0:# and orders_status.Data[1][-1] == 'Normal':
        if len(w_status.Fields) != 3 and w_info['TradeSide'] == 'Buy':
            ord6 = w.torder(Symbol, 'SellToday', close - gap, unit, 'OrderType=BOC,logonid=' + str(LogonId) + '\'')
            print(ord6)
        elif len(w_status.Fields) != 3 and w_info['TradeSide'] == 'Short':
            ord7 = w.torder(Symbol, 'CoverToday', close + gap, unit, 'OrderType=BOC,logonid=' + str(LogonId) + '\'')
            print(ord7)


def trade_loop():
    pre_signal = 0
    while True:
        now_time = datetime.now()
        if '09:00:00' <= now_time.strftime('%H:%M:%S') < '11:30:00' or '13:30:00' <= now_time.strftime('%H:%M:%S') < '15:00:00' or '21:00:00' <= now_time.strftime('%H:%M:%S') < '23:00:00':
            RT_price = get_RT_price()
            td_info = RT_trade(RT_price)
            print(td_info)
            with open(LOG_FILE, 'a') as file_log:
                file_log.write(str(td_info))

            go_trade(pre_signal,td_info[-1], td_info[1])
            pre_signal = td_info[-1]
            sleep(15)
        elif (now_time.strftime('%H:%M:%S') > '11:30:00' and now_time.strftime('%H:%M:%S') < '13:29:00') or (now_time.strftime('%H:%M:%S') > '15:00:00' and now_time.strftime('%H:%M:%S') < '21:00:00'):
            print('Midday, breaking sleep: ' + now_time.strftime('%H:%M:%S'))
            sleep(60)
        elif now_time.strftime('%H:%M:%S') > '23:01:00':
            print('Market is closed today.')
            with open(LOG_FILE, 'a') as file_log:
                w_query = w.tquery(0)
                file_log.write(str(Show(w_query)))
            break
        else:
            now_time = now_time + timedelta(seconds=5)
            print('Not trading time: ' + now_time.strftime('%H:%M:%S'))
            sleep(5)


trade_init()
# trade_loop()