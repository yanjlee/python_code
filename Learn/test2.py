import time
total = 400
print('--- Process starting...')
start = time.perf_counter()
for i in range(total + 1):
    c = int((i / total) * 100)
    a = '#' * int(c/2)
    b = '.' * (50 - int(c/2))    
    time_cost = time.perf_counter() - start
    print("\r{:^3.0f}%: [{}{}] Time cost: {:.2f}s".format(c,a,b,time_cost),end='')
    time.sleep(0.1)
print('\n' + '--- Process end.')
