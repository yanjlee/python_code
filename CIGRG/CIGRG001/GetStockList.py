# -*- coding: utf-8 -*-
"""
@author: GuoJun
"""
from CIGRG.CIGRG001.StockPool import stock_list
# import logging as log
from ConnectDB import get_all_data
import prettytable as pt
import re
import urllib.request

# # BASE_DIR = os.path.dirname(__file__)
# # LOG_PATH = BASE_DIR +'/log/data_update/'
# # LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))) + '.log'
# log.basicConfig(
#     # filename = LOG_PATH + LOG_FILENAME,
#     level=log.DEBUG,
#     # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
#     format="%(levelname)s: %(message)s")

##############################
MONEY = 1500000

def get_data(k_list):
    items = 'symbol, name, industry'
    table = 'stk_info'
    condition = ' where symbol in (' + str(k_list).replace('[', '').replace(']', '') + ') order by symbol'
    stk_data = get_all_data(items, table, condition)
    k_str = str(k_list).replace('[', '').replace(']', '').replace('.SZ\'', '').replace('.SH\'', '').replace('\'00', 's_sz00').replace('\'30', 's_sz30').replace('\'60', 's_sh60').replace(' ', '')
    request_url = 'http://qt.gtimg.cn/q=' + k_str
    headers = {'User-Agent': 'Mozilla/10 (compatible; MSIE 1.0; Windows NT 4.0)'}

    try:
        request = urllib.request.Request(request_url, headers=headers)
        response = urllib.request.urlopen(request).read().decode('gbk')
        reobj = re.compile('v_s_s.*?~.*?~')
        realtemp = reobj.sub('', response).replace('~~";', '').replace('\n', '~').strip().split('~')
        # log.info(realtemp)
        stk_price = {}
        for i in range(0, len(realtemp) - 1, 8):
            if realtemp[i].startswith('6'):
                stk_price[realtemp[i] + '.SH'] = float(realtemp[i + 1])
            else:
                stk_price[realtemp[i] + '.SZ'] = float(realtemp[i + 1])
    except Exception as e:
        print(e)

    stk_volume = {}
    for j in stk_price:
        stk_volume[j] = int(MONEY / len(stk_price) / stk_price[j] / 100) * 100

    stk_info = []
    for k in range(0, len(stk_data)):
        temp = list(stk_data[k])
        temp.insert(0, str(k+1))
        stk_info.append(temp)
        stk_info[k].append(stk_price[stk_data[k][0]])
        stk_info[k].append(stk_volume[stk_data[k][0]])
        print('status, content = client.SendOrder(0, 4, sInvestorID_' + stk_data[k][0][-2:] + ', "' + stk_data[k][0][0:6] + '", ' + str(stk_price[stk_data[k][0]]) + ', ' + str(stk_volume[stk_data[k][0]]) + ')')
    return(stk_info)

# status, content = client.SendOrder(0, 4, sInvestorID_SH, "600563", 45.18,300)
def show_table(stk_data):
    tb = pt.PrettyTable()
    tb.field_names = ['No.','Code', 'Name', 'Industry', 'Price', 'Volume']
    for stock in stk_data:
        tb.add_row(stock)
    tb.align = 'l'
    # print(tb)
    return(tb)


def get_b_list():
    items = 'symbol'
    table = 'b_list'
    condition = 'order by symbol'
    symbol_data = get_all_data(items, table, condition)
    b_list = []
    for i in symbol_data:
        b_list.append(i[0])
    return(b_list)


def main():
    # currentDate = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    items = 'max(date)'
    table = 'idx_price'
    condition = ' where symbol =\'000001.SH\' group by symbol'
    idx_data = get_all_data(items, table, condition)
    currentDate = idx_data[0][0].strftime('%Y-%m-%d')
    # currentDate='2018-06-15'
    stk_list, all_list = stock_list(currentDate)
    b_list = get_b_list()
    stk_list = list(set(stk_list).difference(set(b_list)))
    stk_data = get_data(stk_list)
    tb = show_table(stk_data)
    print(tb)
    print(all_list)
    return(str(tb) + '\n' + str(all_list))


if __name__ == "__main__":
    main()

