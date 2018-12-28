# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from datetime import timedelta, datetime
import pandas as pd
from ConnectDB import get_all_data
from decimal import Decimal
import numpy as np
import scipy as sp
from scipy.optimize import leastsq
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

i = '002456.SZ'
items = 'open, high, low, close'
table = 'stk_price_forward'
condition = 'where symbol = \'' + i + '\' and date >= \'2018-06-01\' order by date asc'
symbol_data = get_all_data(items, table, condition)

# 标准化数据
x_list = []
y_list = []
for i in range(0, len(symbol_data)):
    x_list.append(i)
    ace = Decimal('0.1') * (symbol_data[i][1] + symbol_data[i][2]) + Decimal('0.3') * symbol_data[i][0] + Decimal('0.5') * symbol_data[i][3]
    y_list.append(ace)


price_dt = pd.DataFrame(list(symbol_data), columns=['open','high','low','close'])

y_t = np.array(y_list)
A = np.array(price_dt).T
b = y_t.reshape(y_t.shape[0], 1)


def projection(A, b):
    AA = A.T.dot(A)  # A乘以A转置
    w = np.linalg.inv(AA).dot(A.T).dot(b)
    # print w#w=[[-0.03027851][ 0.1995869 ] [ 2.43887827] [ 1.28426472][-5.60888682] [-0.98754851][ 2.78427031]]
    return A.dot(w)


yw = projection(A, b)
yw.shape = (yw.shape[0],)
#
# plt.plot(x_list, y_list, color='g', linestyle='-', marker='.', label='ACE')
# # # plt.plot(x,y,color='g',linestyle='-',marker='',label=u'理想曲线')
# plt.plot(x_list, b, color='m', linestyle='', marker='o', label='PriceData')
# plt.plot(x_list, yw, color='b', linestyle='-', marker='.', label="Simu_line")
# # # 把拟合的曲线在这里画出来
# plt.legend(loc='upper left')
# plt.show()

# x = np.arange(-1,1,0.02)
# y = ((x*x-1)**3+1)*(np.cos(x*2)+0.6*np.sin(x*1.3))
# y1 = y+(np.random.rand(len(x))-0.5) ################################## ### 核心程序 #使用函数y=ax^3+bx^2+cx+d对离散点进行拟合，最高次方需要便于修改，所以不能全部列举，需要使用循环 #A矩阵
# m=[]
# for i in range(7):#这里选的最高次为x^7的多项式
#     a=x**(i)
#     m.append(a)
# A=np.array(m).T
# b=y1.reshape(y1.shape[0],1) ##################################
#
# def projection(A,b):
#     AA = A.T.dot(A)#A乘以A转置
#     w=np.linalg.inv(AA).dot(A.T).dot(b)
#     # print w#w=[[-0.03027851][ 0.1995869 ] [ 2.43887827] [ 1.28426472][-5.60888682] [-0.98754851][ 2.78427031]]
#     return A.dot(w)
#
# yw = projection(A,b)
# yw.shape = (yw.shape[0],)

# plt.plot(x,y,color='g',linestyle='-',marker='',label=u"理想曲线")
# plt.plot(x,y1,color='m',linestyle='',marker='o',label=u"已知数据点")
# plt.plot(x,yw,color='r',linestyle='',marker='.',label=u"拟合曲线")
# plt.legend(loc='upper left')
# plt.show()