# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import random

b= 0
for c in range(0,10000):
    a = 0
    for i in range(0,10000):
        a = a + random.randint(1,6)

    print(c)
    if a > 35500:
        b=b+1
print(b/10000)