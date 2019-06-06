# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta, datetime as dt
import talib as ta
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import numpy as np
from STK.tsdata import get_k_stk as get_k, get_stk, get_stk_1h, get_cb

# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

def Run(sym,cci_n, dataset):
    #实参数据定义##########################
    FEE = 0
    units = 2000

    def MaxDrawDown(return_list):
        max_value = 0
        mdd = 0
        for i in return_list:
            max_value = max(i, max_value)
            if max_value != 0:
                mdd = round(min(mdd, (i - max_value) / max_value),3)
            else:
                mdd = 0
        return(mdd)


    # 获取数据, 创建DataFrame

    df = dataset.set_index('datetime')

    # 定义账户类
    class ActStatus:
        def __init__(self):
            self.datetime = ''
            self.close = 0
            self.chg = 0
            self.pos = 0 # 1 long，-1 short，0 empty
            self.pre_pos = 0

            self.pnl = 0
            self.fee = 0
            self.net_pnl = 0
            self.pnl_rate = 0

        def trade_calc(self, datetime, close, chg, signal, pre_pos):
            self.datetime =datetime
            self.close = close
            self.chg = chg
            self.pos = signal
            self.pre_pos = pre_pos

            self.pnl = self.chg * self.pos * units * self.close
            self.fee = max(abs(self.close * units * abs(self.pos - self.pre_pos)) * FEE, 5 * abs(self.pos - self.pre_pos))
            self.net_pnl = self.pnl - self.fee
            self.pnl_rate = (self.chg - FEE) * self.pos


    # 策略和类初始化数据
    signal = 0
    pre_pos = 0
    rt_list = []
    atr = df.atr.iloc[0]
    pre_close = df.close.iloc[0]
    max_price = 0
    buy_price = 0
    b_day = 0

    cci_col = []
    for c in cci_n:
        cci_col.append('cci' + str(c))
    pre_cci_list = list(df[cci_col].iloc[0])

    for i, row in enumerate(df.iterrows()):
        datetime = row[0]
        close = row[1].close
        chg = row[1].chg
        atr = row[1].atr
        cci_list = list(row[1][cci_col])
        b_day = max(b_day - 1, 0)

        if i < 1:  # 从第二条开始
            continue

    ## 数据与信号驱动计算
        rt = ActStatus()
        rt.trade_calc(datetime, close, chg, signal, pre_pos)
        rt_list.append(rt)
        pre_pos = rt.pos


    ## 策略信号
        signal_list =[]

        ## CCI策略
        for j in range(0, len(cci_n)):
            pre_cci = pre_cci_list[j]
            cci = cci_list[j]
            ci = 101
            range_value = 50
            for i in range(-ci, ci + 300, range_value):
                if pre_cci < i and cci > i:
                    signal_list.append(1)
                elif pre_cci > i and cci < i:
                    signal_list.append(-1)
                else:
                    signal_list.append(pre_pos)

        signal_value = sum(signal_list) # 计算产生总信号
        if signal_value > 0:
            signal = 1
        elif signal_value < 0:
            signal = 0
        else:
            signal = pre_pos

        # # ATR 止损
        # if signal == 1:
        #     max_price = max(max_price, row[1].high)
        # else:
        #     max_price = 0
        #
        # if close < (max_price - 2.2 * atr) and signal == 1:
        #     signal = 0
        # elif b_day != 0:
        #     signal = 0

        # 百分比止损
        stop_loss = 0.05
        if signal == 1 and close < buy_price * (1 - stop_loss):
            signal = 0
        if pre_pos == 0 and signal == 1:
            buy_price = pre_close
        elif pre_pos == 1 and signal == 0:
            buy_price = 0
            b_day = 3

        ## 保留前一天close数据
        pre_close = close
        pre_cci_list = cci_list

    # 结果统计与展示
    df_rt = pd.DataFrame()
    df_rt['datetime'] = [rt.datetime for rt in rt_list]
    # df_rt['close'] = [rt.close for rt in rt_list]
    # df_rt['chg'] = [rt.chg for rt in rt_list]
    # df_rt['pos'] = [rt.pos for rt in rt_list]
    # df_rt['pre_pos'] = [rt.pre_pos for rt in rt_list]
    # df_rt['pnl'] = [rt.pnl for rt in rt_list]
    # df_rt['fee'] = [rt.fee for rt in rt_list]
    df_rt.index = [rt.datetime for rt in rt_list]
    df_rt['pnl_rate'] = [rt.pnl_rate for rt in rt_list]
    df_rt['cum_rate'] = round(df_rt['pnl_rate'].cumsum().astype(float) + 1,3)
    df_rt['raw_cret'] = round(df['chg'].cumsum().astype(float) + 1, 3)
    max_draw_down = MaxDrawDown(df_rt['cum_rate'])
    ax = df_rt[['cum_rate', 'raw_cret']].plot(title= sym )
    fig = ax.get_figure()
    fig.savefig(sym + '_cci.png')
    df_rt = df_rt.set_index('datetime')

    return(df_rt.cum_rate.iloc[-1], max_draw_down,df_rt)


def DrawSignals(k_data):
    # 作图
    stick_freq = 20 # 横坐标间隔

    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(k_data[['datetime','open','high','low','close']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(ndays)

    left, width = 0.05, 0.90 ## 定义图横向使用
    rect1 = [left, 0.48, width, 0.50] ## 第一框图高度从0.48~0.98
    rect3 = [left, 0.28, width, 0.20] ## 第二框图高度从0.28~0.48，余下留给了横坐标
    rect2 = [left, 0.08, width, 0.20] ## 第3框图高度从0.08~0.28，余下留给了横坐标

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax)
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)
    ax2t = ax2.twinx() ## 右侧镜像纵坐标

    ax3.plot(date_strings, k_data['ii'], color='red', label='II%')
    ax3.plot(date_strings, k_data['ad%'], color='green', label='AD%')
    ax3.plot(date_strings, k_data['mfi'] / 100 - 0.5, color='blue', label='MFI')
    ax3.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.axhline(0.15, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.legend(loc='upper left', frameon=False)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['bp'] * 100, color='red', label='bp%')
    # ax2.plot(date_strings, k_data['mfi'], color='blue', label='mfi')
    # ax2.plot(date_strings, k_data['cci'], color='blue', label='cci')
    ax2.legend(loc='upper left', frameon=False)

    ax2t.set_ylim(float(min(k_data.cci)), float(max(k_data.cci)))
    ax2t.plot(date_strings, k_data['cci'], color='green', label='cci')
    ax2t.legend(loc='upper right', frameon=False)
    ax2t.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2t.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    ax.plot(date_strings, k_data['ma'], color='m', label='MA')
    ax.plot(date_strings, k_data['up'], color='blue', label='Bolling_up')
    ax.plot(date_strings, k_data['down'], color='brown', label='Bolling_down')
    # ax.plot(date_strings, k_data['sar'], marker = '*',color='olive', label='SAR', lw=0.5)
    ax.legend(loc='upper left', frameon=False)

    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化
    ax2.grid(True, linestyle='dotted', linewidth='0.5')
    ax3.grid(True, linestyle='dotted', linewidth='0.5')

    for label in ax.get_xticklabels():
        label.set_visible(False) ## 隐藏第一框图横坐标
    for label in ax3.get_xticklabels():
        label.set_visible(False)  ## 隐藏第一框图横坐标
    plt.show()

def DrawSignals2(k_data):
    # 作图
    stick_freq = 20 # 横坐标间隔

    ## 数据清理，去除非交易时间
    ohlc_data_arr = np.array(k_data[['datetime','open','high','low','close']])
    ohlc_data_arr2 = np.hstack([np.arange(ohlc_data_arr[:, 0].size)[:, np.newaxis], ohlc_data_arr[:, 1:]])
    ndays = ohlc_data_arr2[:, 0]  # array([0, 1, 2, ... n-2, n-1, n])
    date_strings = list(ndays)

    left, width = 0.05, 0.90 ## 定义图横向使用
    rect1 = [left, 0.48, width, 0.50] ## 第一框图高度从0.48~0.98
    rect3 = [left, 0.28, width, 0.20] ## 第二框图高度从0.28~0.48，余下留给了横坐标
    rect2 = [left, 0.08, width, 0.20] ## 第3框图高度从0.08~0.28，余下留给了横坐标

    fig = plt.figure(facecolor='white')
    axescolor = '#f6f6f6'  # the axes background color

    ax = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
    ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax)
    ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax)

    ax3.plot(date_strings, k_data['cum_rate'], color='blue', label='c_return')
    ax3.axhline(1, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax3.legend(loc='upper left', frameon=False)

    ax2.set_xticklabels(date_strings[::stick_freq], rotation=30, ha='right') ## 定义横坐标格式
    ax2.plot(date_strings, k_data['cci30'], color='green', label='cci30')
    ax2.plot(date_strings, k_data['cci60'], color='red', label='cci60')
    ax2.legend(loc='upper left', frameon=False)
    ax2.axhline(100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2.axhline(0, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线
    ax2.axhline(-100, linestyle='dotted', color='m', lw=1)  ## 画一条水平收益基准线

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, width=0.6, colorup='r', colordown='g') ## K线图绘制

    # Format x axis
    ax.set_xticks(ndays[::stick_freq])
    ax.set_xticklabels(date_strings[::stick_freq], rotation=0, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())
    ax.legend(loc='upper left', frameon=False)
    ax.autoscale_view()
    ax.grid(True, linestyle='dotted', linewidth='0.5') ## 背景格线虚化
    ax2.grid(True, linestyle='dotted', linewidth='0.5')
    ax3.grid(True, linestyle='dotted', linewidth='0.5')

    for label in ax.get_xticklabels():
        label.set_visible(False) ## 隐藏第一框图横坐标
    for label in ax3.get_xticklabels():
        label.set_visible(False)  ## 隐藏第一框图横坐标
    plt.show()

def ta_cci(n, k_data):
    cci = pd.DataFrame()
    cci['cci'+str(n)] = ta.CCI(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return cci.round(2)

def ta_atr(n, k_data):
    atr = pd.DataFrame()
    atr['atr'] = ta.ATR(k_data.high, k_data.low, k_data.close, timeperiod=n)
    return(atr.round(3))


def zscore(dataset):
    dict_data = dataset
    z_values = {}
    data_mean = np.mean(list(dict_data.values()))
    data_std = np.std(list(dict_data.values()))
    for k, v in dict_data.items():
        z_values[k] = round((v-data_mean)/data_std,3)
    # return z_values
    return dict(sorted(z_values.items(), key=lambda x: x[1], reverse=True))


def zscore_list(dataset):
    list_data = dataset
    z_values = []
    data_mean = np.mean(list_data)
    data_std = np.std(list_data)
    for i in list_data:
        z_values.append(round((i-data_mean)/data_std,3))
    # return z_values
    return z_values


total_return = []
return_m = []

# symbol_list = ['SHSE.510880','SZSE.159901','SZSE.159915','SHSE.518880','SZSE.159919','SHSE.510900','SHSE.511260','SHSE.513500','SHSE.510050','SHSE.510500']
# symbol_list = ['SHSE.512880']
# symbol_list = ['SHSE.600000','SHSE.600009','SHSE.600010','SHSE.600011','SHSE.600015','SHSE.600016','SHSE.600018','SHSE.600019','SHSE.600023','SHSE.600027','SHSE.600028','SHSE.600029','SHSE.600030','SHSE.600031','SHSE.600036','SHSE.600038','SHSE.600048','SHSE.600050','SHSE.600061','SHSE.600066','SHSE.600068','SHSE.600085','SHSE.600089','SHSE.600104','SHSE.600109','SHSE.600111','SHSE.600115','SHSE.600118','SHSE.600153','SHSE.600170','SHSE.600176','SHSE.600177','SHSE.600196','SHSE.600208','SHSE.600271','SHSE.600273','SHSE.600276','SHSE.600297','SHSE.600332','SHSE.600340','SHSE.600346','SHSE.600352','SHSE.600362','SHSE.600369','SHSE.600372','SHSE.600383','SHSE.600388','SHSE.600398','SHSE.600406','SHSE.600415','SHSE.600436','SHSE.600438','SHSE.600482','SHSE.600487','SHSE.600489','SHSE.600498','SHSE.600516','SHSE.600518','SHSE.600519','SHSE.600522','SHSE.600535','SHSE.600547','SHSE.600549','SHSE.600566','SHSE.600570','SHSE.600583','SHSE.600585','SHSE.600588','SHSE.600606','SHSE.600612','SHSE.600637','SHSE.600660','SHSE.600674','SHSE.600688','SHSE.600690','SHSE.600703','SHSE.600705','SHSE.600739','SHSE.600741','SHSE.600760','SHSE.600795','SHSE.600809','SHSE.600816','SHSE.600837','SHSE.600867','SHSE.600886','SHSE.600887','SHSE.600893','SHSE.600900','SHSE.600909','SHSE.600919','SHSE.600926','SHSE.600958','SHSE.600977','SHSE.600987','SHSE.600998','SHSE.600999','SHSE.601006','SHSE.601009','SHSE.601012','SHSE.601018','SHSE.601021','SHSE.601088','SHSE.601108','SHSE.601111','SHSE.601117','SHSE.601155','SHSE.601166','SHSE.601169','SHSE.601186','SHSE.601198','SHSE.601211','SHSE.601225','SHSE.601229','SHSE.601238','SHSE.601288','SHSE.601318','SHSE.601328','SHSE.601333','SHSE.601336','SHSE.601360','SHSE.601377','SHSE.601390','SHSE.601398','SHSE.601555','SHSE.601601','SHSE.601607','SHSE.601611','SHSE.601618','SHSE.601628','SHSE.601668','SHSE.601669','SHSE.601688','SHSE.601727','SHSE.601766','SHSE.601788','SHSE.601800','SHSE.601818','SHSE.601857','SHSE.601877','SHSE.601888','SHSE.601899','SHSE.601901','SHSE.601919','SHSE.601933','SHSE.601939','SHSE.601985','SHSE.601988','SHSE.601989','SHSE.601992','SHSE.601997','SHSE.601998','SHSE.603288','SHSE.603799','SHSE.603833','SHSE.603858','SHSE.603898','SHSE.603993','SZSE.000001','SZSE.000002','SZSE.000063','SZSE.000069','SZSE.000100','SZSE.000157','SZSE.000166','SZSE.000333','SZSE.000338','SZSE.000402','SZSE.000413','SZSE.000423','SZSE.000425','SZSE.000538','SZSE.000568','SZSE.000625','SZSE.000627','SZSE.000630','SZSE.000651','SZSE.000661','SZSE.000671','SZSE.000709','SZSE.000725','SZSE.000728','SZSE.000768','SZSE.000776','SZSE.000783','SZSE.000792','SZSE.000826','SZSE.000839','SZSE.000848','SZSE.000858','SZSE.000876','SZSE.000887','SZSE.000895','SZSE.000898','SZSE.000938','SZSE.000961','SZSE.000963','SZSE.000983','SZSE.001979','SZSE.002001','SZSE.002007','SZSE.002008','SZSE.002024','SZSE.002027','SZSE.002032','SZSE.002044','SZSE.002050','SZSE.002065','SZSE.002081','SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002153','SZSE.002179','SZSE.002202','SZSE.002230','SZSE.002236','SZSE.002241','SZSE.002271','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002304','SZSE.002310','SZSE.002311','SZSE.002352','SZSE.002415','SZSE.002422','SZSE.002450','SZSE.002456','SZSE.002460','SZSE.002466','SZSE.002475','SZSE.002493','SZSE.002508','SZSE.002555','SZSE.002558','SZSE.002572','SZSE.002594','SZSE.002601','SZSE.002602','SZSE.002624','SZSE.002673','SZSE.002714','SZSE.002736','SZSE.002773','SZSE.002797','SZSE.002833','SZSE.300003','SZSE.300015','SZSE.300017','SZSE.300024','SZSE.300033','SZSE.300059','SZSE.300070','SZSE.300072','SZSE.300122','SZSE.300124','SZSE.300136','SZSE.300142','SZSE.300144','SZSE.300251','SZSE.300296','SZSE.300408','SZSE.300433']
symbol_list = ['110030','110031','110033','110034','110038','110039','110040','110041','110042','110043','110044','110045','110046','110047','110048','110049','110050','110051','110052','110053','110054','110055','110056','110057','110058','113008','113009','113011','113012','113013','113014','113015','113016','113017','113018','113019','113020','113021','113022','113024','113025','113026','113502','113503','113504','113505','113506','113507','113508','113509','113510','113511','113512','113513','113514','113515','113516','113517','113518','113519','113520','113521','113522','113523','113524','113525','113526','113527','113528','113529','113530','113531','113532','113533','113534','113535','123001','123002','123003','123004','123005','123006','123007','123008','123009','123010','123011','123012','123013','123014','123015','123016','123017','123018','123019','123020','123021','123022','123023','123024','123025','127003','127004','127005','127006','127007','127008','127009','127010','127011','127012','127013','128010','128012','128013','128014','128015','128016','128017','128018','128019','128020','128021','128022','128023','128024','128025','128026','128027','128028','128029','128030','128032','128033','128034','128035','128036','128037','128038','128039','128040','128041','128042','128043','128044','128045','128046','128047','128048','128049','128050','128051','128052','128053','128054','128055','128056','128057','128058','128059','128060','128061','128062','128063','128064','128065','128066','128067','132004','132005','132007','132008','132009','132011','132013','132014','132015','132017','132018']
types = '5'

# s_time = '2018-12-01'
# e_time = '2019-05-07'
# years = int(e_time[:4]) - int(s_time[:4]) + 1
# start_year = s_time
# end_year = e_time

und_avg = []
und_std = []
up_std = []
dn_std = []
symbols = []
for sym in symbol_list:
# 查询历史行情
#     df_k = history(symbol=sym, frequency='1d', start_time=start_year, end_time=end_year, fields='eob,open,high,low,close,volume',adjust=1, df=True)
#     df_k = get_stk(sym, start_year, end_year)
    df_k = get_cb(sym, types)
    # df_k = get_stk_1h(sym, 60, 0, start_year, end_year)
    if len(df_k) == 0:
        continue
    # df_k.loc[:, 'chg'] = (df_k['close'] - df_k['close'].shift(1)) / df_k['close'].shift(1)
    df_k.loc[:, 'und'] = (df_k['high'] - df_k['low']) / df_k['close']
    # df_k.loc[:, 'up'] = (df_k['high'] - 0.5 * (df_k['open'] + df_k['close'])) / df_k['close']
    # df_k.loc[:, 'dn'] = (0.5 * (df_k['open'] + df_k['close']) - df_k['low']) / df_k['close']
    symbols.append(sym)
    und_avg.append(df_k.und.mean())
    und_std.append(df_k.und.std())
    # up_std.append(df_k.up.std())
    # dn_std.append(df_k.dn.std())

df_std = pd.DataFrame({'symbol':symbols,'und_avg':und_avg,'und_std':und_std,'avg_z':zscore_list(und_avg),'std_z':zscore_list(und_std)})#,'up_std':up_std,'dn_std':dn_std})
df_std = df_std.sort_values(by='avg_z' , ascending=False)
print(df_std)

# frame.sort(columns = ['a'],axis = 0,ascending = False)
# avg_z = zscore(avg)
# std_z = zscore(std)
# for k,v in avg_z.items():
#     print(k + ': ' + str(v))
##def, 近30条k线的std或者mean，多只股票放在一起进行标准化排序，分组进行风格测试

    # k_data =  pd.concat([df_k, ta_atr(20,df_k), cci_m], axis=1)
    # k_data = k_data.dropna()
    # DrawSignals(k_data)

    # re, mdd, df_r = Run(sym,cci_n, k_data)
    # k_data = k_data.set_index('datetime')
    # k_data = pd.concat([k_data,df_r], axis=1)
    # k_data = k_data.reset_index('datetime')
    # DrawSignals2(k_data)
    # print([sym, start_year, end_year, re, mdd])
    # print(str(k_data.datetime.iloc[0]) + ' ~ ' + str(k_data.datetime.iloc[-1]))
    # total_return.append([sym, start_year, end_year, re, mdd])

# ret = pd.DataFrame(total_return, columns=['symbol', 'start', 'end', 'return', 'mdd'])
# print(ret)
# ret.plot()

# filename = dt.now().strftime('%Y%m%d_%H%M%S') + '.csv'
# # t_r=pd.DataFrame(list(return_m))
# # t_r.to_csv(filename)
# t_s=pd.DataFrame(list(total_return))
# t_s.to_csv('R'+filename)

# statMatrx = pd.DataFrame()
# for sy in symbol_list:
#     for st in start_list:
#         queryStr = 'start==\'' + st + '\'&symbol==\'' + sy + '\''
#         test = ret.query(queryStr)
#         test['efc'] = (test['return']-1) / - test.mdd
#         test2 = test.groupby('f')
#         test3 =test2.mean()
#         test3.reset_index('f')
#         statMatrx=statMatrx.append(test3)
#
# statMatrx.to_csv('test_f.csv')
# test4 = statMatrx.groupby('f')
# test5 = test4.mean()
# test5.to_csv('calc_f.csv')

