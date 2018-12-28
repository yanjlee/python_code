# coding=utf-8
import easytrader
import helpers
import pandas as pd
import easyquotation
from connect_db import get_all_data
import time

def init():
    user=easytrader.use('ht_client')
    user.prepare('C:/codes/easytrader/account.json')
    user.refresh()
    ipo_data = helpers.get_today_ipo_data()
    print(ipo_data)
    # if len(ipo_data) > 0:
    #     ipo_info = user.auto_ipo()
    #     print(ipo_info)
    # balance, position = account(user)
    return(user)

def account(user):
    user.refresh()
    try:
        balance = user.balance
        balance = user.balance
        position = user.position
        position = user.position
        position = pd.DataFrame(position)
        position = position.drop(['Unnamed: 14','股东帐户','交易市场','冻结数量','在途数量'],  axis=1, inplace=False)
    except Exception as e:
        pass
    return(balance, position)

def balance(user):
    user.refresh()
    balance = user.balance
    balance = user.balance
    return(balance)

def position(user):
    try:
        position = user.position
        position = user.position
        position = pd.DataFrame(position)
        position = position.drop(['Unnamed: 14','股东帐户','交易市场','冻结数量','在途数量'],  axis=1, inplace=False)
    except Exception as e:
        pass
    return(position)

def order_all(user):
    user.refresh()
    try:
        orders = user.today_entrusts
        orders = user.today_entrusts
        orders = pd.DataFrame(orders)
        orders = orders.drop(['Unnamed: 13','股东帐户','交易市场'],  axis=1, inplace=False)
    except Exception as e:
        pass
    return(orders)

def trade_all(user):
    user.refresh()
    try:
        trade = user.today_trades
        trade = user.today_trades
        trade = pd.DataFrame(trade)
        trade = trade.drop(['Unnamed: 11','股东帐户','交易市场'],  axis=1, inplace=False)
    except Exception as e:
        pass
    return(trade)

def get_price(symbol_list):
    symbols= []
    for i in symbol_list:
        symbols.append(i.replace('SHSE.','').replace('SZSE.',''))
    qt = easyquotation.use('sina')
    raw_data = qt.stocks(symbols)
    s_data = []
    for k, v in raw_data.items():
        s_data.append([k, v['ask1'],v['ask1_volume'],v['bid1'],v['bid1_volume']])
    s_data = pd.DataFrame(s_data, columns = ['symbol','ask_1','ask_1_v','bid_1','bid_1_v'])
    return(s_data)


def get_vol(symbol_list):
    items = 'symbol, vol_usage'
    table = 'act_pos'
    condition = 'where symbol in (' + str(symbol_list).replace('[','').replace(']','') + ') and vol_usage > 0'
    vol_data = dict(get_all_data(items,table,condition))
    return(vol_data)

def get_money():
    items = 'money'
    table = 'act_info'
    condition = ' '
    money = get_all_data(items, table, condition)
    money = money[0][0]
    return(money)

def buy(symbol_list,user):
    b_list = []
    for i in symbol_list:
        b_list.append(i.replace('SHSE.','').replace('SZSE.',''))
    vol_data = get_vol(b_list)
    b_list = list(set(b_list) ^ set(list(vol_data.keys())))
    p_data = get_price(b_list)
    p_data = dict(list(zip(list(p_data.symbol), list(p_data.bid_1))))
    money = get_money()
    for symbol in b_list:
        vol_data[symbol] = int(money/len(b_list)/100/p_data[symbol]) * 100
    for k,v in p_data.items():
        print('Buy--' + k + ', price--' + str(v) + ', vol--' + str(vol_data[k]))
        user.buy(k,v,vol_data[k])


def sell(symbol_list,user):
    s_list = []
    for i in symbol_list:
        s_list.append(i.replace('SHSE.','').replace('SZSE.',''))
    vol_data = get_vol(s_list)
    p_data = get_price(list(vol_data.keys()))
    p_data = dict(list(zip(list(p_data.symbol), list(p_data.ask_1))))
    for k,v in vol_data.items():
        print('Sell--' + k + ', price--' + str(p_data[k]) + ', vol--' + str(v))
        user.sell(k,p_data[k],v)


def trade_exe(s_list, b_list):
    user = init()
    if len(s_list) > 0:
        sell(s_list, user)
        time.sleep(15)
    if len(b_list) > 0:
        buy(b_list, user)




# user.buy('162411', price=0.55, amount=100)
# user.sell('162411', price=0.55, amount=100)
# user.auto_ipo()
# user.cancel_entrust('buy/sell 获取的 entrust_no')
#
# user.today_trades # 当日成交
# user.today_entrusts # 当日委托
#
# # 查询今天可以申购的新股信息
# from easytrader import helpers
# ipo_data = helpers.get_today_ipo_data()
# print(ipo_data)
#
#
# # 退出客户端软件
# user.exit()
#
#
# # 远端服务器模式
# # 在服务器上启动服务#
# from easytrader import server#
# server.run(port=1430) # 默认端口为 1430#
# # 远程客户端调用#
# from easytrader import remoteclient
# user = remoteclient.use('使用客户端类型，可选 yh_client, ht_client 等', host='服务器ip', port='服务器端口，默认为1430')


