# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
from ConnectDB import connDB, connClose, get_all_data, get_data
import logging as log
import datetime, time
import prettytable as pt

# BASE_DIR = os.path.dirname(__file__)
LOG_PATH = 'D:/temp/log/'
LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))) + '.log'
log.basicConfig(
    filename=LOG_PATH + LOG_FILENAME,
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")


#####################################

def get_data(symbol, table):
    items = 'max(date) as date'
    table = table
    condition = ' where symbol =  \'' + symbol + '\''
    db_data = get_all_data(items, table, condition)
    db_info = [symbol, table, db_data[0][0].strftime('%Y-%m-%d')]
    return (db_info)


def main():
    db_list = {'159901.OF': 'etf_price', '000001.SH': 'idx_price',
               '000001.SZ': 'stk_price', '000002.SZ': 'stk_price_forward', '600036.SH': 'stk_price_backward',
               '002456.SZ': 'stk_ratio', '000002.SH': 'idx_price_tec','000001.SZ': 'stk_price_tec'}
    db_info = []
    for i in db_list:
        temp = get_data(i, db_list[i])
        db_info.append(temp)

    tb = pt.PrettyTable()
    tb.field_names = ['Code', 'Table', 'Date']
    for stock in db_info:
        tb.add_row(stock)
    tb.align = 'l'
    print(tb)
    return(tb)


if __name__ == "__main__":
    tb = main()
