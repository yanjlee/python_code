import baostock as bs
import pandas as pd
import numpy as np
import talib as ta
import datetime


# 获取历史行情数据，并根据日K线数据设置警示价格
def return_constraintdict(stockcodelist):
    login_result = bs.login(user_id='anonymous', password='123456')
    print('login respond error_msg:' + login_result.error_msg)

    startdate = '2018-01-01'
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    # 获取截至上一个交易日的历史行情
    predate = today - delta
    strpredate = datetime.datetime.strftime(predate, '%Y-%m-%d')

    for stockcode in stockcodelist:
        ### 获取沪深A股行情和估值指标(日频)数据并返回收盘价20日均线 ####
        #     date    日期
        #     code    股票代码
        #     close    收盘价
        #     preclose    前收盘价
        #     volume    交易量
        #     amount    交易额
        #     adjustflag    复权类型
        #     turn    换手率
        #     tradestatus 交易状态
        #     pctChg    涨跌幅
        #     peTTM    动态市盈率
        #     psTTM    市销率
        #     pcfNcfTTM    市现率
        #     pbMRQ    市净率
        rs = bs.query_history_k_data("%s" % stockcode,
                                     "date,code,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                     start_date=startdate, end_date=strpredate,
                                     frequency="d", adjustflag="2")
        print('query_history_k_data respond error_code:' + rs.error_code)
        print('query_history_k_data respond  error_msg:' + rs.error_msg)

        #### 打印结果集 ####
        result_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)

        closelist = list(result['close'])
        closelist = [float(price) for price in closelist]

        malist = ta.MA(np.array(closelist), timeperiod=20)
        if len(malist) > 20 and closelist[-20] > 0:
            ma20value = malist[-1]
            summit20day = max(closelist[-10:])
            # 以突破10日高点且在20日均线以上作为买入条件
            resistancelinedict[stockcode] = max(ma20value, summit20day)
        else:
            resistancelinedict[stockcode] = float(closelist[-1])
    bs.logout()
    return resistancelinedict


# 每次收到实时行情后，回调此方法
def callbackFunc(ResultData):
    print(ResultData.data)
    for key in ResultData.data:
        # 当盘中价格高于警示价格，输出提示信息。
        if key in resistancelinedict and float(ResultData.data[key][6]) > resistancelinedict[key]:
            print("%s,突破阻力线，可以买入" % key)


def test_real_time_stock_price(stockcode):
    login_result = bs.login_real_time(user_id='anonymous', password='123456')
    # 订阅
    rs = bs.subscribe_by_code(stockcode, 0, callbackFunc, "", "user_params")
    #     rs = bs.subscribe_by_code("sz.300009", 0, callbackFunc, "", "user_params")
    if rs.error_code != '0':
        print("request real time error", rs.error_msg)
    else:
        # 使主程序不再向下执行。使用time.sleep()等方法也可以
        text = input("press any key to cancel real time \r\n")
        # 取消订阅
        cancel_rs = bs.cancel_subscribe(rs.serial_id)
    # 登出
    login_result = bs.logout_real_time("anonymous")


if __name__ == '__main__':
    resistancelinedict = {}
    # stockcodes = "sh.600000,sz.300009,sz.300128,sh.603568,sz.000049"
    stockcodelist = ['sh.600000', 'sz.300009', 'sz.300128',
                     'sh.603568', 'sz.000049', 'sh.600518', 'sz.300532', 'sz.000001']
    stockcodes = ""
    for stockcode in stockcodelist:
        stockcodes = "%s%s," % (stockcodes, stockcode)
    stockcodes = stockcodes[:-1]
    print(stockcodes)
    resistancelinedict = return_constraintdict(stockcodelist)
    #### 登出系统 ####
    test_real_time_stock_price(stockcodes)