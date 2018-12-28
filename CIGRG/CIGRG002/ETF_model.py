import urllib.request
from termcolor import colored, cprint
import re
from ConnectDB import connDB, connClose, get_data, get_all_data
from datetime import date, datetime, timedelta
import logging as log

log.basicConfig(
    # filename = LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

pd_list = [3,5, 20, 22, 30]
universe = (
    '159901.OF', '159902.OF', '159905.OF', '159915.OF', '159920.OF', '159938.OF', '159949.OF', '510050.OF', '510180.OF',
    '510230.OF', '510300.OF', '510500.OF', '510880.OF', '510900.OF', '511010.OF', '512660.OF', '512800.OF', '512880.OF',
    '512980.OF', '512990.OF', '513050.OF', '513100.OF', '518880.OF')


# universe = ('512000','510880','510500','513500','513100','159901','510160','510900') #定义Universe

class Message:
    def info(self, info):
        self.info = info


# 获取Universe内所有指数实时价格
headers = {'User-Agent': 'Mozilla/10 (compatible; MSIE 1.0; Windows NT 4.0)'}
codes = str(universe).replace('\'', '').replace(', 1', ',s_sz1').replace(', 5', ',s_sh5').replace('(', '').replace(')',
                                                                                                                   '').replace(
    '.OF', '')
url = 'http://qt.gtimg.cn/q=s_sz' + codes

try:
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request).read().decode('gbk')
    reobj = re.compile('v_s_s.*?~.*?~')
    realtemp = reobj.sub('', response).replace('~~";', '').replace('\n', '~').strip().split('~')
    rt_price = {}
    rt_chg = {}
    for i in range(0, len(realtemp) - 1, 6):

        rt_price[realtemp[i] + '.OF'] = float(realtemp[i + 1])
        rt_chg[realtemp[i] + '.OF'] = float(realtemp[i + 3])
except Exception as e:
    print(e)
#
# #获取datelist所列回溯日期收盘价
if datetime.now().date().weekday() in range(0, 5) and int(datetime.now().strftime('%H%M%S')) in range(93001, 150000):
    limit = max(pd_list)
else:
    limit = max(pd_list) + 1
items = 'date'
tables = 'idx_price'
condition = ' where symbol = \'399300.SZ\' order by date desc limit ' + str(limit)
date_info = get_all_data(items, tables, condition)
# logging.info(sqlcontent)
#
tempdays = []
for i in pd_list:
    tempdays.append(date.isoformat(date_info[i - 1][0]))
days = tuple(tempdays)

items = 'symbol, date, close'
tables = 'etf_price'
condition = ' where symbol in ' + str(universe) + ' and date in ' + str(days) + ' order by date, symbol'
price_info = get_all_data(items, tables, condition)
content = {}
for i in days:
    daily_price = {}
    for k in price_info:
        if i == date.isoformat(k[1]):
            daily_price[k[0]] = k[2]
    content[i] = daily_price

items = 'symbol, name'
tables = 'etf_info'
condition = ' where symbol in ' + str(universe)
etf_info = get_all_data(items, tables, condition)
etf_name = dict(etf_info)

# 计算Return
pd_return = {}
try:
    for i in content:
        tempreturn = {}
        for k in content[i]:
            tempreturn[k] = round(100 * (rt_price[k] / float(content[i][k]) - 1), 2)
            pd_return[i] = tempreturn
except Exception as e:
    print(e)

# #打印标题
Message.info = ''
size = 25
title = 'ETF动量轮动策略： ' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(title)
Message.info += title + '\n'

# 预定义指数与ETF关系
temp = sorted(days, reverse=True)
temp.reverse()
#
week_day = pd_return[temp[-1]]
temp.pop()
#
# 输出计算结果
for i in temp:
    lines = '-' * (size - 10) + i + '-' * (size + 10)
    Message.info += lines + '\n'
    print(lines)
    return_temp = sorted(pd_return[i].items(), key=lambda d: d[1], reverse=True)

    for n in range(0, 11):
        temp = str(n + 1) + ' .  ' + str(return_temp[n][0]) + ' ' + str(etf_name[return_temp[n][0]]) + ': ' + str(
            return_temp[n][1]) + '%'
        temp2 = ' | D: ' + str(rt_chg[return_temp[n][0]]) + '%'
        temp3 = ' | W: ' + str(week_day[return_temp[n][0]]) + '%'
        #
        if return_temp[n][1] > 0:
            cprint(temp, 'green', end="")
        else:
            cprint(temp, 'white', end="")

        if rt_chg[return_temp[n][0]] <= -3:
            cprint(temp2, 'red', end="")
        else:
            cprint(temp2, 'white', end="")

        if week_day[return_temp[n][0]] <= -5:
            cprint(temp3, 'red')
        else:
            cprint(temp3, 'white')

        Message.info += temp + '\n'
