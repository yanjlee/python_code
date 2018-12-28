'''
????????????GUI??????????????????????????????????????????.
???????????1???????????????????????????????logonID??????????????е???????.
         ??2??????дGUI???е??????LogonID?????????????????????м??????????, ?????.
'''

from PyQt4 import QtGui,uic
from CIGRG.WindPy import *
w.start()

qtCreatorFile="sample.ui" #Enter file,????QT??ν???
Ui_MainWindow,QtBaseClass = uic.loadUiType(qtCreatorFile)

global accountNumber;
accountNumber=0

class MyApp(QtGui.QMainWindow,Ui_MainWindow): 
    def __init__(self):
      
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.accountLogin.clicked.connect(self.login)        #"??????"??????
        self.torder.clicked.connect(self.torderProcess)      #"??????"??????
        self.quit.clicked.connect(self.logout)               #"??????"??????

    #????????, ??????ID
    def login(self):
        
        global accountNumber;
        for k in range(2):
            accountlabelName="account_label"+str(k)
            exec("temtText=self."+accountlabelName+".text()")
            if temtText!="":
                windLogin=w.tlogon('0000','0',str(temtText),'123456','SHSZ') 
                exec('self.LogonID_label'+str(k)+'.setText(str(windLogin.Data[0][0]))')
                print windLogin
            accountNumber=k+1          

    #????????
    def torderProcess(self):
        tmp=[]
        for j in range(5):
            tmp.append("")
            table_info = []
            for i in range(5):
                table_info.append(tmp)
    
        for i in range(5):
            labelName="label"+str(i)+"_"+str(0)
            exec("temtText=self."+labelName+".text()")
            if(len(temtText)!=0):
                for j in range(5):
                    labelName="label"+str(i)+"_"+str(j)
                    exec("temtText=self."+labelName+".text()")
                    if(len(temtText)!=0):
                        table_info[i][j]=str(temtText)
                torderResult=w.torder(table_info[i][1],table_info[i][2],table_info[i][3],table_info[i][4],'OrderType=LMT;LogonID='+table_info[i][0])

    #????????
    def logout(self):
        global accountNumber;
        if accountNumber!=0:
            for i in range(1,accountNumber):
                w.tlogout(i)
                print i
        self.close()       

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())



