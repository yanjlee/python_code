import sys,time
count = 0
lst =400 
for i in range(lst):
    count = count + 1
##    sys.stdout.write("#")
    sys.stdout.write("\r当前进度: {:.2f}%".format(count*100/lst))
    sys.stdout.flush()  ##随时刷新到屏幕上
    time.sleep(0.1)
    
#import time
#import sys
#for i in range(101):
#    sys.stdout.write("\r%s%% |%s" %(int(i%101), int(i%101)*'#'))
#    sys.stdout.flush()
#    time.sleep(0.5)
# 
#sys.stdout.write('\n')
