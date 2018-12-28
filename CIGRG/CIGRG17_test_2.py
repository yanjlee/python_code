# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 11:00:41 2018

@author: lpeng
"""

import pandas as pd
import numpy as np
from CIGRG.WindPy import w
import datetime
from pandas import DataFrame

w.start()

'''以下模块主要用于寻找期货换月日期'''
startdate=(datetime.date.today()-datetime.timedelta(365*4)).strftime('%Y%m%d')
enddate=(datetime.date.today()).strftime('%Y%m%d')

i=w.wsd("I.DCE", "trade_hiscode,close",startdate, enddate, "")
i_data=DataFrame(i.Data,index=['i_HISCODE','CLOSE'],columns=i.Times).T


def find_change_index(data):
    dif_index=[]
    for i in range(1,len(data)):
        if data[i]!=data[i-1]:
           dif_index.append(i)
    return dif_index     

i_change_index=find_change_index(i_data.i_HISCODE)

def unique(data):
    dt=[]
    for  i in range(len(data)):       
        if data[i] not in dt:
          dt.append(data[i])
          continue
    return np.array(dt)

i_change_index=find_change_index(np.array(i_data.iloc[:,0]))

change_date=pd.DatetimeIndex(i_data.index)[list(np.array(i_change_index)-1)]
         
change_date=pd.DatetimeIndex(i_data.index)[list(np.array(i_change_index)-1)]
future_change_date=[i.strftime('%Y%m%d') for i in change_date]
#################################################################################


N1=10 #均线周期
N2=30 #均线周期
N3=60 #均线周期
BarSize='30' #交易的周期，即按照30分钟周期
unit=100 #合约单位，铁矿1手100吨
equity=100000 #1起始资金


winddata=w.wsi("I.DCE", "close", "2016-03-01 09:00:00", "2018-03-02 15:00:00", "BarSize="+BarSize,"periodstart=09:00:00;periodend=23:30:00") #读取分钟数据
itime=[i.strftime('%Y%m%d %H:%M:%S') for i in winddata.Times ]
I_data=DataFrame(winddata.Data[0],index=itime,columns=['I_30min'])


mean_10=pd.rolling_mean(np.array(I_data),N1)[N3:]#10日均线
mean_30=pd.rolling_mean(np.array(I_data),N2)[N3:]#30日均线
mean_60=pd.rolling_mean(np.array(I_data),N3)[N3:]#60日均线
i_data=I_data[N3:]

length=len(i_data)#测试数据长度
holding=[] #持仓，1表示做多，-1做空 0表示空仓
open_price=[]#记录开仓价格
pro=[] #记录每次交易盈亏
trade_num=0 #记录交易次数，开仓平仓算一次交易
fee=10 #手续费，目前是按照2手手续费，即2手5块钱
signal=[] #交易信号，做多1 做空-1 没有信号0
for i in range(length):
    if mean_10[i]>mean_30[i]  and mean_10[i]>mean_60[i]:
        signal.append(1)
    if mean_10[i]<mean_30[i]  and mean_10[i]<mean_60[i]:  
        signal.append(-1)
    else:
        signal.append(0)

#第一次如果交易
if signal[0]==1 and i_data.index[0][:8] not in future_change_date:#多头开仓
    holding.append(1)
    open_price.append(i_data.iloc[0,0])
    pro.append(-fee)
    #Profit.append(pro)
if signal[0]==-1 and i_data.index[0][:8] not in future_change_date: #空头开仓
    holding.append(-1)
    open_price.append(i_data.iloc[0,0])
    pro.append(-fee)
    #Profit.append(pro)
else:  #空仓
    holding.append(0)
    open_price.append(0)
    pro.append(0)
    #Profit.append(pro)
i_data.iloc[i,0]>mean_10[i] and (i_data.iloc[i-1,0]>mean_30[i-1] and i_data.iloc[i,0]<mean_30[i])
    

for i in range(1,length):
    print(i)
    
    if signal[i]==1 and i_data.index[i][:8] not in future_change_date and holding[-1]==1:
        holding.append(1)
        open_price.append(open_price[-1])
        pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2)
        #Profit.append(pro)
        print('铁矿石多头继续持仓')
        continue
        
    if  signal[i]==-1 and i_data.index[i][:8] not in future_change_date and holding[-1]==-1:
        holding.append(-1)
        open_price.append(open_price[-1])
        pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2)
        #Profit.append(pro)
        print('铁矿石空头继续持仓')
        continue
    if  signal[i]==-1 and i_data.index[i][:8] not in future_change_date and holding[-1]==1:
        holding.append(-1)
        open_price.append(i_data.iloc[i,0])
        pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
        #Profit.append(pro)
        print('铁矿石多头翻空头')
        continue
    if  signal[i]==1 and i_data.index[i][:8] not in future_change_date and holding[-1]==-1:
        holding.append(1)
        open_price.append(i_data.iloc[i,0])
        pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
        #Profit.append(pro)
        print('铁矿石空头翻多头')
        continue
    if  signal[i]==1 and i_data.index[i][:8] not in future_change_date and holding[-1]==0:
        holding.append(1)
        open_price.append(i_data.iloc[i,0])
        pro.append(-fee)
        #Profit.append(pro)
        print('在空仓的情况下铁矿石多头开仓')
        continue
    if  signal[i]==-1 and i_data.index[i][:8] not in future_change_date and holding[-1]==0:
        holding.append(-1)
        open_price.append(i_data.iloc[i,0])
        pro.append(-fee)
        #pro[i]=Profit.append(pro)
        print('在空仓的情况下铁矿石空头开仓')
        continue
    if  signal[i]==0 and i_data.index[i][:8] not in future_change_date and holding[-1]==0:
        holding.append(0)
        open_price.append(0)
        pro.append(0)
        #Profit.append(pro)
        print('在空仓的情况下继续空仓')
        continue
    if signal[i]==0 and i_data.index[i][:8] not in future_change_date and holding[-1]==1:
        if  i_data.iloc[i,0]>mean_10[i] and (i_data.iloc[i-1,0]>mean_30[i-1] and i_data.iloc[i,0]<mean_30[i]) :
            holding.append(0)
            open_price.append(0)
            pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
            #Profit.append(pro)
            trade_num=trade_num+1
            print("铁矿石已经持有多单出现信号0平仓出场")
        else:
             holding.append(1)
             open_price.append(open_price[-1])
             pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
             print("铁矿石持有多单但是出现信号为0的情况下继续持仓")
    
    if signal[i]==0 and i_data.index[i][:8] not in future_change_date and holding[-1]==-1:
        if  i_data.iloc[i,0]<mean_10[i] and (i_data.iloc[i-1,0]<mean_30[i-1] and i_data.iloc[i,0]>mean_30[i]):
                holding.append(0)
                pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
                #pro.append(0)
                #Profit.append(pro)
                print('铁矿石已经持有空单出现信号0平仓出场')
                continue 
        else:
             holding.append(-1)
             open_price.append(open_price[-1])
             pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
             print("铁矿石持有空单但是出现信号为0的情况下继续持仓")
             continue
    
    if   i_data.index[i][:8] not in future_change_date and holding[-1]==1 and i_data.iloc[i,0]<open_price[-1]*0.98: 
        holding.append(0)
        open_price.append(0)
        pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
        
        #Profit.append(pro)
        trade_num=trade_num+1
        print("铁矿石多单止损出场")
        print(pro[-1])
    if   i_data.index[i][:8] not in future_change_date and holding[-1]==1 and i_data.iloc[i,0]>open_price[-1]*1.04: 
        holding.append(0)
        open_price.append(0)
        pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
        #Profit.append(pro)
        trade_num=trade_num+1
        print("铁矿石多单止盈出场")
        print(pro[-1])
        continue
    if  i_data.index[i][:8] not in future_change_date and holding[-1]==-1 and i_data.iloc[i,0]>open_price[-1]*1.02: 
        holding.append(0)
        open_price.append(0)
        pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)        
        trade_num=trade_num+1
        #Profit.append(pro)
        print("铁矿石空单止损失出场")
        print(pro[-1])
        continue
    if  i_data.index[i][:8] not in future_change_date and holding[-1]==-1 and i_data.iloc[i,0]<open_price[-1]*0.96: 
        holding.append(0)
        open_price.append(0)
        pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2-fee)
        
        #Profit.append(pro)
        trade_num=trade_num+1
        print("铁矿石空单止盈出场")
        print(pro[-1])
        continue 
    if  i_data.index[i][:8]  in future_change_date:
        if holding[-1]==0:
            holding.append(0)
            open_price.append(0)
            pro.append(0)
            #Profit.append(pro)
            
            print("铁矿石空仓换月")
        if holding[-1]==1:            
             holding.append(0)          
             open_price.append(0)   
             pro.append((i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2)
             trade_num=trade_num+1
             print("铁矿石多头换月")
           
        if holding[-1]==-1:             
              holding.append(0)          
              open_price.append(0)   
              pro.append(-(i_data.iloc[i,0]-i_data.iloc[i-1,0])*unit*2)
              trade_num=trade_num+1
              print("铁矿石空头即将换月")
           
    '''else:
        holding.append(0)
        open_price.append(0)
        pro.append(0)
        print("没有考虑到的情况")'''
               
#账户资金权益变化
equity_day=np.cumsum(pro)+equity            
 
#收益率曲线           
title='profit of CIGRG17 with I :'+str((equity_day[-1]/equity)-1)            
DataFrame(np.cumsum(pro),columns=['equity ']).plot(title=title)    
        
 
#计算最大回撤       
def cal_max_back(mon):
    max_back=[]
    for i in range(len(mon)):
       max_equity=mon[:i+1].max()
       if max_equity==mon[i]:
            max_back.append(0)
       else:
            max_back.append((mon[i]-max_equity)/max_equity)  
    #print(max_back)
    return  max_back

back_ratio=cal_max_back(equity_day) 

title='max_back of CIGRG17 with I :'+str(min(back_ratio))
DataFrame(back_ratio,columns=['back_ratio']).plot(color='red',title=title)       
         
        
        
       
        
        
        
        
        
    
