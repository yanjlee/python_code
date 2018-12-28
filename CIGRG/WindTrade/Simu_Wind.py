# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
# from PyQt4 import QtCore,QtGui,uic
from CIGRG.WindPy import *
import prettytable as pt

w.start()

def Show(querty_data):
    tb = pt.PrettyTable()
    tb.field_names = querty_data.Fields
    temp = []
    for i in querty_data.Data:
        temp.append(i[0])
    tb.add_row(temp)
    tb.align = 'l'
    print(tb)
    # return(tb)

# Login = w.tlogon('0000', '0', 'W3184800401', 'g66196619', 'SHSZ')
## 登陆
Login = w.tlogon('0000', '0', 'W3184800402', 'g66196619', 'CFE')
Show(Login)


w_query = w.tquery(0)
Show(w_query)

