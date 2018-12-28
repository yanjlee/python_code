# -*- coding:utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import *
from PyQt4.QtCore import pyqtSlot as Slot
import ui_quote
import wsq
import globaldef
from CIGRG.WindPy import w
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas # matplotlib对PyQt4的支持
from matplotlib.figure import Figure

w.start()

MAC = True
try:
    from PyQt4.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False


class QuoteDlg(QDialog,
               ui_quote.Ui_Dialog):

    def __init__(self, parent=None):
        super(QuoteDlg, self).__init__(parent)
        self.setupUi(self)
        self.sec1Edit.setFocus()
        self.setWindowTitle("Wind API Demo---WSQ Subscrib")
        self.updateUi()
        self.initGraph()

    def initGraph(self):
        self.scene = QGraphicsScene()
        self.dr = Figure_Canvas()
        self.scene.addWidget(self.dr)
        self.graphicsView.setScene(self.scene)

    @Slot()
    def on_subscribeButton_clicked(self):
        self.subscribeButton.setEnabled(False)
        self.cancelButton.setEnabled(True)
        self.textBrowser.clear()
        globaldef.secID = []
        globaldef.indID = []
        globaldef.secID.extend([unicode(self.sec1Edit.text()).upper(),unicode(self.sec2Edit.text()).upper()])
        globaldef.indID.extend([unicode('rt_time').upper(),unicode('rt_bid1').upper(),unicode('rt_ask1').upper(),
                      unicode('rt_bsize1').upper(),unicode('rt_asize1').upper(),unicode('rt_last').upper()])
        self.qThread = wsq.feeder()
        self.qThread.start()
        self.qThread.update_data.connect(self.handle_display)
        self.qThread.update_data.connect(self.handle_graphic)

    def handle_display(self , data):
        #Update UI
        self.last1Edit.setText(QString(str(data[0][5])))
        self.last2Edit.setText(QString(str(data[1][5])))
        self.bidvol1Edit.setText(QString(str(data[0][3])))
        self.bidvol2Edit.setText(QString(str(data[1][3])))
        self.bid1Edit.setText(QString(str(data[0][1])))
        self.bid2Edit.setText(QString(str(data[1][1])))
        self.ask1Edit.setText(QString(str(data[0][2])))
        self.ask2Edit.setText(QString(str(data[1][2])))
        self.askvol1Edit.setText(QString(str(data[0][4])))
        self.askvol2Edit.setText(QString(str(data[1][4])))
        self.spread1Edit.setText(QString(str(globaldef.spreadBid)))
        self.spread2Edit.setText(QString(str(globaldef.spreadAsk)))
        self.textBrowser.append("<b>%s</b> | Spd_Bid:<b>%s</b> | Spd_Ask:<b>%s</b>|"
                                %(str(data[0][0])[0:6],str(globaldef.spreadBid),str(globaldef.spreadAsk)))

    def handle_graphic(self,data):
        self.dr.plot()

    @Slot()
    def on_cancelButton_clicked(self):
        self.subscribeButton.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.qThread.finished()

    @Slot(QString)
    def on_sec1Edit_textEdited(self,text):
        self.updateUi()

    @Slot(QString)
    def on_sec2Edit_textEdited(self,text):
        self.updateUi()

    def updateUi(self):
        enable=not self.sec1Edit.text().isEmpty() and not self.sec2Edit.text().isEmpty()
        self.subscribeButton.setEnabled(enable)
        self.cancelButton.setEnabled(enable)


class Figure_Canvas(FigureCanvas):
    # 通过继承FigureCanvas类，使得该类既是一个PyQt4的Qwidget
    # 又是一个matplotlib的FigureCanvas，这是连接pyqt4与matplotlib的关键
    def __init__(self, parent=None, width=7.4, height=5, dpi=100):
        # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig) # 初始化父类
        self.setParent(parent)
        # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        self.axes1 = fig.add_subplot(311)
        self.axes2 = fig.add_subplot(312)
        self.axes3 = fig.add_subplot(313)

        #FigureCanvas.setSizePolicy(self,
        #                           QSizePolicy.Expanding,
        #                           QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)

    def plot(self):
        self.axes1.plot(globaldef.plotLast)
        self.axes1.hold(False)
        self.axes1.grid(True)
        self.axes1.xaxis.set_visible(False)
        self.axes1.set_title("Real Time Spread_Last Trend Graph", fontsize=10)
        self.axes2.plot(globaldef.plotBid)
        self.axes2.hold(False)
        self.axes2.grid(True)
        self.axes2.xaxis.set_visible(False)
        self.axes2.set_title("Real Time Spread_Bid Trend Graph", fontsize=10)
        self.axes3.plot(globaldef.plotAsk)
        self.axes3.hold(False)
        self.axes3.grid(True)
        self.axes3.set_title("Real Time Spread_Ask Trend Graph", fontsize=10)
        self.draw()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = QuoteDlg()
    form.show()
    app.exec_()