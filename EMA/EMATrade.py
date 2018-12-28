1# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from time import sleep
from CIGRG.WindPy import *
import prettytable as pt
import requests
import re

#######################
Symbol = 'rb1810.SHF'
gap = 0.5
unit =1
close_list = ['000553.SZ', '000596.SZ', '000681.SZ', '000977.SZ', '002050.SZ', '002065.SZ', '002153.SZ', '002262.SZ', '002299.SZ', '002410.SZ', '002422.SZ', '002507.SZ', '002563.SZ', '002690.SZ', '002727.SZ', '002821.SZ', '300003.SZ', '300144.SZ', '300166.SZ', '300253.SZ', '300347.SZ', '300529.SZ', '600031.SH', '600270.SH', '600271.SH', '600380.SH', '600436.SH', '600673.SH', '600760.SH', '600763.SH', '600771.SH', '600779.SH', '600809.SH', '600845.SH', '600872.SH', '600884.SH', '600967.SH', '601799.SH', '601901.SH', '603228.SH', '603369.SH', '603568.SH', '603658.SH', '603883.SH']
total_money = 9500000
#######################


w.start()

# # logger配置
# BASE_DIR = os.path.dirname(__file__)
# LOG_PATH = BASE_DIR + '/logs/'
# LOG_FILENAME = 'CIGRG_005_' + datetime.now().strftime('%Y%m%d') + '.log'
# LOG_FILE = LOG_PATH + LOG_FILENAME
#
# # 创建一个logger
# logger = log.getLogger('my_log')
# logger.setLevel(log.DEBUG)
#
# # 创建一个handler，用于写入日志文件
# output_file = log.FileHandler(LOG_PATH + LOG_FILENAME)
# output_file.setLevel(log.DEBUG)
#
# # 再创建一个handler，用于输出到控制台
# console_info = log.StreamHandler()
# console_info.setLevel(log.DEBUG)
#
# # 定义handler的输出格式
# formatter = log.Formatter('[%(levelname)s] %(message)s')
# output_file.setFormatter(formatter)
# console_info.setFormatter(formatter)
#
# # 给logger添加handler
# logger.addHandler(output_file)
# logger.addHandler(console_info)

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
    # with open(LOG_FILE, 'a') as file_log:
    #     start_message = '******Initialize trading on ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     print(start_message)
    #     file_log.write(start_message)

        # Login = w.tlogon('0000', '0', 'W3184800401', 'g66196619', 'SHSZ')
        ## 登陆
        Login = w.tlogon('0000', '0', 'W3184800401', 'g66196619', 'SHSZ')
        # file_log.write(str(Show(Login)))
        w_query = w.tquery(0) # 查询账户基本信息
        # file_log.write(str(Show(w_query)))


    # return account, trade_price


def get_RT_price():
    global total_money
    stk_list = []
    for i in close_list:
        if i.endswith('.SZ',6,9):
            stk_list.append('sz' + i.replace('.SZ',''))
        else:
            stk_list.append('sh' + i.replace('.SH',''))

    get_sina_url = 'http://hq.sinajs.cn/list=' + str(stk_list).replace('[','').replace(']','').replace('\'','').replace(' ','')
    get_current_data = requests.get(get_sina_url).text.split('var hq_str_')
    del get_current_data[0]

    trading_data  = []
    for i in get_current_data:
        temp = i.split(',')
        if temp[0].startswith('sz',0,3):
            temp[0] = re.sub('=.*','.SZ',temp[0].replace('sz',''))
        else:
            temp[0] = re.sub('=.*','.SH',temp[0].replace('sh',''))
        trading_data.append([ temp[0], float(temp[3]), 100 * int(total_money/len(close_list)/float(temp[3])/100)])
    return trading_data

trade_init()
Login = w.tquery('LogonID')
global LogonId
LogonId = Login.Data[0][0]
w_status = w.tquery('Position', 'logonid=' + str(LogonId) + ',Windcode=' + Symbol + '\'')
trade_info = get_RT_price()
for i in trade_info:
    w.torder(i[0], 'Buy', i[1] + 0.1, i[2], 'OrderType=LMT,logonid=' + str(LogonId) + '\'')



def RT_trade(RT_price):
    global close_list
    close_list.append(RT_price[1])
    if len(close_list) > 20:
        del close_list[0]
    elif len(close_list) == 1:
        close_list = close_list * 20

    ace = round(0.1 * (max(close_list[-8:]) + min(close_list[-8:])) + 0.3 * close_list[-8] + 0.5 * close_list[-1], 2)
    ema5 = round(close_list[-1] / 3 + 4 * close_list[15] / 15 + close_list[11] / 5 + 2 * close_list[7] / 15 + close_list[3] / 15, 2)

    if ace > ema5:
        signal = -1
    elif ace == ema5:
        signal = 0
    elif ace < ema5:
        signal = 1
    else:
        signal = 0

    if datetime.now().strftime('%H:%M:%S') > '14:55:00' or datetime.now().strftime('%H:%M:%S') < '09:35:00':
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
        if '09:30:00' <= now_time.strftime('%H:%M:%S') < '11:30:00' or '13:00:00' <= now_time.strftime('%H:%M:%S') < '15:00:00':
            RT_price = get_RT_price()
            td_info = RT_trade(RT_price)
            print(td_info)
            with open(LOG_FILE, 'a') as file_log:
                file_log.write(str(td_info))

            go_trade(pre_signal,td_info[-1], td_info[1])
            pre_signal = td_info[-1]
            sleep(15)
        elif now_time.strftime('%H:%M:%S') > '11:30:00' and now_time.strftime('%H:%M:%S') < '12:59:00':
            print('Midday, breaking sleep: ' + now_time.strftime('%H:%M:%S'))
            sleep(60)
        elif now_time.strftime('%H:%M:%S') > '15:03:00':
            print('Market is closed today.')
            with open(LOG_FILE, 'a') as file_log:
                w_query = w.tquery(0)
                file_log.write(str(Show(w_query)))
            break
        else:
            now_time = now_time + timedelta(seconds=5)
            print('Not trading time: ' + now_time.strftime('%H:%M:%S'))
            sleep(5)


# trade_init()
# trade_loop()