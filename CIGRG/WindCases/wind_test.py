# encoding: utf-8

from CIGRG.WindPy import *
import time

def start():
    w.start()
    time.sleep(5)
    print ('after w.start()')
    data = w.wsi("A.DCE", "KDJ", "2015-09-01 09:00:00", "2015-09-30 08:50:00", "KDJ_N=9;KDJ_M1=3;KDJ_M2=3;KDJ_IO=1;BarSize=5")
    time.sleep(5)
    print ('after w.wsi')
    print (data)
    w.stop()
    time.sleep(10)


if __name__ == '__main__':
    start()