'''
功能：批量下单GUI，账户股票多账户下单，注意下单前修改价格与登录号是否合理.
操作流程：第1步：用户登录自己的股票账户，返回登录号（logonID），可参照例子中的登录函数.
         第2步：填写GUI的中的登录号（LogonID）、股票代码、买卖方向、委托价格和委托数量, 并下单.
'''

from CIGRG import WindPy as w
from PyQt4 import QtGui,uic
from CIGRG.WindPy import *
w.start()

qtCreatorFile="sample.ui" #Enter file,导入QT图形界面
Ui_MainWindow,QtBaseClass = uic.loadUiType(qtCreatorFile)

global accountNumber;
accountNumber=0

class MyApp(QtGui.QMainWindow,Ui_MainWindow): 
    def __init__(self):
      
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.accountLogin.clicked.connect(self.login)        #"登陆账户"按钮事件
        self.torder.clicked.connect(self.torderProcess)      #"开始下单"按钮事件
        self.quit.clicked.connect(self.logout)               #"退出下单"按钮事件

    #登陆多账户, 返回登陆ID
    def login(self):
        
        global accountNumber;
        for k in range(2):
            accountlabelName="account_label"+str(k)
            exec("temtText=self."+accountlabelName+".text()")
            if temtText!="":
                windLogin=w.tlogon('0000','0',str(temtText),'123456','SHSZ') 
                exec('self.LogonID_label'+str(k)+'.setText(str(windLogin.Data[0][0]))')
                print(windLogin)
            accountNumber=k+1          

    #多账户下单
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

    #登出多账户
    def logout(self):
        global accountNumber;
        if accountNumber!=0:
            for i in range(1,accountNumber):
                w.tlogout(i)
                print (i)
        self.close()       

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())



