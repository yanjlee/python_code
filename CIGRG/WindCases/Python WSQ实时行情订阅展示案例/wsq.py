# -*- coding:utf-8 -*-
from CIGRG.WindPy import w
import globaldef
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSignal as Signal

w.start()


class feeder(QThread):
    update_data = Signal(object)
    #def __init__(self,threadID,name):
    #    QThread.Thread.__init__(self)
    #    self.threadID = threadID
    #    self.name = name
    def run(self):
        w.start()
        secstring = ",".join(globaldef.secID)
        indstring = ",".join(globaldef.indID)
        w.wsq(secstring, indstring, func=self.myCallback)

    def finished(self):
        w.cancelRequest(0)

    def myCallback(self,indata):
        if indata.ErrorCode != 0:
            print('error code:' + str(indata.ErrorCode) + '\n')
            return ()

        for j in range(0, len(indata.Fields)):
            indindex = globaldef.indID.index(indata.Fields[j])
            for k in range(0, len(indata.Codes)):
                if indata.Codes[k] == globaldef.secID[0]:
                    globaldef.gdata[0][indindex] = indata.Data[j][k]
                if indata.Codes[k] == globaldef.secID[1]:
                    globaldef.gdata[1][indindex] = indata.Data[j][k]
                #R如果订阅的SecID较多，可以用下面方式获取数据
                #codeindex = globaldef.secID.index(indata.Codes[k])
                #globaldef.gdata[codeindex][indindex] = indata.Data[j][k]
        globaldef.spreadBid = globaldef.gdata[0][2] - globaldef.gdata[1][1]
        globaldef.spreadAsk = globaldef.gdata[0][1] - globaldef.gdata[1][2]
        globaldef.spreadLast = globaldef.gdata[0][5] - globaldef.gdata[1][5]
        globaldef.plotLast.append(globaldef.spreadLast)
        globaldef.plotBid.append(globaldef.spreadBid)
        globaldef.plotAsk.append(globaldef.spreadAsk)
        self.update_data.emit(globaldef.gdata)

        print("-----------------------------------")
        print(indata)
