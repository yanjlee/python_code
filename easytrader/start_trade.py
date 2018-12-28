# coding=utf-8
from datetime import datetime as dt
import time
import ts_data as td


symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600585','SHSE.600508','SHSE.600660','SHSE.603288']
frequency_1m = '60s'
frequency_1h = '3600s'
count = 1
current_time = dt.now().strftime('%H:%M:%S') #  获取当前时间

# 初始化，更新数据到最新
start = dt.now().strftime('%Y-%m-%d ') + '09:29:00'
end = dt.now().strftime('%Y-%m-%d %H:%M:%S')
td.update_gm_history(frequency_1m,'ts_price_1m',symbol_list,start,end)
td.update_gm_history(frequency_1h,'ts_price_1h',symbol_list,start,end)
td.update_calc_data(symbol_list)


while current_time < '09:30:00': # 早盘前, 判断非交易时间则休眠并循环
    print('****' + current_time + ': 尚未开始交易，请着好准备并等待至9点30分开盘。')
    if current_time < '09:29:00':
        time.sleep(60)
    time.sleep(5)
    current_time = dt.now().strftime('%H:%M:%S')

# 交易时间(包括午休)
while current_time >= '09:30:00' and current_time <= '15:01:00':
    if current_time >= '11:30:00' and current_time <= '12:59:00':
        print('****' + current_time + ': 午盘，休息时间。')
        time.sleep(60)
    elif current_time > '12:59:00' and current_time < '13:00:00':
        print('****' + current_time + ': 午休结束，准备下午盘开始吧！')
        time.sleep(5)
    else:  # 交易时间循环
        # 1. 更新1m、1h、cci数据
        td.get_gm_data(symbol_list,'ts_price_1m', frequency_1m, count) # 获取1分钟数据,并插入ts_price_1m数据库
        if current_time[:5] in ['10:30','11:30','14:00','15:00']:
            td.get_gm_data(symbol_list, 'ts_price_1h', frequency_1h, count)  # 获取1小时数据,并插入ts_price_1h数据库
            td.update_calc_data(symbol_list) # 计算CCI策略及其交易信号, 并插入td_cci数据表
        
        #2. 实时更新交易信号
        print('****交易时间: ' + current_time + '***********************************')
        if current_time[:5] in ['09:30','10:30','13:00','14:00']:
            signal_list = td.get_cci_signal_h(symbol_list)
        else:           
            signal_list = td.get_cci_signal(symbol_list)
        print(signal_list)

        time.sleep(15) # 间隔多少合适呢？

    # 决策，调用easyTrade，发出指令
    # 检查交易反馈数据
    current_time = dt.now().strftime('%H:%M:%S')

while current_time > '15:01:00': # 收盘, 判断非交易时间则休眠并循环
    start = dt.now().strftime('%Y-%m-%d ') + '09:29:00'
    end = dt.now().strftime('%Y-%m-%d ') + '15:01:00'
    td.update_gm_history(frequency_1m,'ts_price_1m',symbol_list,start,end)
    td.update_gm_history(frequency_1h,'ts_price_1h',symbol_list,start,end)
    td.update_calc_data(symbol_list)
    print('****' + current_time + ': 已收市，请关闭自动交易程序，检查今日交易数据与总结分析。')
    time.sleep(3000)
    current_time = dt.now().strftime('%H:%M:%S')