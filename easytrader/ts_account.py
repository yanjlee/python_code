# coding=utf-8
import ht_trade as ht
# import time
from datetime import datetime as dt
from connect_db import fill_data
from ts_data import *
from datetime import datetime as dt
import time
import os

n = 10
user = ht.init()


def get_order():
    for i in range(0,n):
        try:
            user.refresh()
            # orders = ht.order_all(user)
            orders = ht.order_all(user)
            if len(orders.columns) == 11:
                break
        except Exception as e:
            pass
        # time.sleep(2)
    return(orders)

def get_pos():
    for i in range(0,n):
        try:
            user.refresh()
            # pos = ht.position(user)
            pos = ht.position(user)
            if len(pos.columns) == 10:
                break
        except Exception as e:
            pass
        # time.sleep(2)
    return(pos)

def get_trade():
    for j in range(0, n):
        try:
            user.refresh()
            # trades = ht.trade_all(user)
            trades = ht.trade_all(user)
            if len(trades.columns == 9):
                break
        except Exception as e:
            pass
        # time.sleep(2)
    return(trades)

def get_balance():
    for k in range(0, n):
        try:
            user.refresh()
            # balance = ht.balance(user)
            balance = ht.balance(user)
            if len(balance.columns > 0):
                break
        except Exception as e:
            pass
        # time.sleep(2)
    return(balance)

def update_info():
    orders = get_order()
    trades = get_trade()
    balance = get_balance()
    pos = get_pos()
    current = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    # insert balance info
    update_act_info = 'insert into act_info values(\'' + current + '\',' + str(balance['总资产']) + ',' + str(balance['股票市值']) + ',' + str(balance['可用金额'])+ ',' + str(balance['冻结资金'])+ ',' + str(balance['可取金额']) + ');'
    try:
        fill_data(update_act_info)
    except Exception as e:
        print(e)
        print(update_act_info)

    # insert orders info
    if len(orders) > 0:
        for i in range(0, len(orders)):
            update_act_order = 'insert into act_order values(' + orders['合同编号'].iloc[i] + ',\'' + dt.isoformat(dt.strptime(str(orders['委托日期'].iloc[i]),'%Y%m%d'))[:10] + ' ' + str(orders['委托时间'].iloc[i]) + '\',\'' + orders['操作'].iloc[i] + '\',\'' + orders['备注'].iloc[i] + '\',\'' + orders['证券代码'].iloc[i] + '\',\'' + orders['证券名称'].iloc[i] + '\','+ str(orders['委托价格'].iloc[i]) + ','+ str(orders['委托数量'].iloc[i]) + ','+ str(orders['成交均价'].iloc[i]) + ','+ str(orders['成交数量'].iloc[i]) + ');'
            try:
                fill_data(update_act_order)
            except Exception as e:
                print(e)
                print(update_act_order)

    # insert trades info
    if len(trades) > 0 :
        for j in range(0, len(trades)):
            update_act_td = 'insert into act_td values(' + str(trades['成交编号'].iloc[j]) + ',' + trades['合同编号'].iloc[j] + ',\'' + dt.isoformat(dt.strptime(str(trades['成交日期'].iloc[j]),'%Y%m%d'))[:10] + '\',\'' + trades['操作'].iloc[j] + '\',\'' + trades['证券代码'].iloc[j] + '\',\'' + trades['证券名称'].iloc[j] + '\','+ str(trades['成交均价'].iloc[j]) + ','+ str(trades['成交数量'].iloc[j]) + ','+ str(trades['成交金额'].iloc[j]) + ');'
            try:
                fill_data(update_act_td)
            except Exception as e:
                print(e)
                print(update_act_td)

    # update position info
    del_all = 'delete from act_pos'
    fill_data(del_all)
    if len(pos) > 0:
        for k in range(0, len(pos)):
            update_act_pos = 'insert into act_pos values(\'' + pos['证券代码'].iloc[k] + '\',\'' + pos['证券名称'].iloc[k] + '\',' + str(pos['股票余额'].iloc[k]) + ',' + str(pos['可用余额'].iloc[k]) + ',' + str(pos['市价'].iloc[k]) + ','+ str(pos['市值'].iloc[k]) + ','+ str(round(pos['成本价'].iloc[k],3)) + ','+ str(round(pos['保本价'].iloc[k],3))+ ','+  str(pos['盈亏比(%)'].iloc[k])+ ','+ str(round(pos['盈亏'].iloc[k],3)) + ');'
            try:
                fill_data(update_act_pos)
            except Exception as e:
                print(e)
                print(update_act_pos)



current_time = dt.now().strftime('%H:%M:%S')
trade_list = ['SZSE.000333','SZSE.002456','SHSE.512880']
# htd.get_price(['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600585','SHSE.600508','SHSE.600660','SHSE.603288','SHSE.603288'])
try:
    trade(trade_list, user)
    os.system("C:/codes/easytrader/Blackberry.m4a")
    time.sleep(60)
except Exception as e:
    print(e)

update_info()
