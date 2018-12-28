# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=

from ConnectDB import connDB, connClose, get_all_data
import urllib.request

# http://finance.sina.com.cn/iframe/futures_info_cff.js
# http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=AL1809
# http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesMiniKLine5m?symbol=IF1809

# i = '002456.SZ'
# items = 'open, high, low, close'
# table = 'stk_price_forward'
# condition = 'where symbol = \'' + i + '\' and date >= \'2018-06-01\' order by date asc'
# symbol_data = get_all_data(items, table, condition)



def Update_Symbol_List():
    symbols_url = 'http://finance.sina.com.cn/iframe/futures_info_cff.js'
    url_page = urllib.request.urlopen(symbols_url).read().decode('gb2312')
    raw_list = [ i for i in url_page.split() if i.startswith('Array(')]
    raw_list.pop(0)
    conn, cur = connDB()
    for j in raw_list:
        insert_sql = 'insert into data.fur_info values' + j.replace('Array','')
        try:
            conn.cursor().execute(insert_sql)
        except Exception as e:
            print(e)
            print(insert_sql)
    conn.commit();
    connClose(conn, cur)


def Get_Future_Price():
    conn, cur = connDB()    
    items = 'a.symbol,b.datetime'
    table = 'fur_info a left join (select symbol, max(datetime) as datetime from data.fur_price_5m group by symbol) b on a.symbol=b.symbol'
    condition = 'order by a.symbol asc'
    list_data = get_all_data(items, table, condition)
    symbol_datetime = dict(list_data)
    for symbol in symbol_datetime.keys():
        if symbol.startswith('IF') or symbol.startswith('IC') or symbol.startswith('IH') or symbol.startswith('TF') or symbol.startswith('TS') or symbol.startswith('T1') :
            symbol_url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesMiniKLine5m?symbol=' + symbol
        else:
            symbol_url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol=' + symbol
    
        symbol_page = urllib.request.urlopen(symbol_url).read().decode('utf-8')
        symbol_data = symbol_page.replace('[[','').replace(']]','').split('],[')
        for k in symbol_data:
            if symbol_datetime[symbol] is not None:
                if k[1:20] <=  symbol_datetime[symbol].strftime('%Y-%m-%d %H:%M:%S'):
                    continue
            insert_sql = 'insert into data.fur_price_5m values(\'' + symbol + '\',' + k + ')'
            try:
                conn.cursor().execute(insert_sql)
            except Exception as e:
                print(e)
                print(insert_sql)
        conn.commit();
    connClose(conn, cur)



Update_Symbol_List()
Get_Future_Price()