# coding=utf-8

from ConnectDB import connDB, connClose
# from datetime import datetime, timedelta
from urllib import request as rq
import json
import time
import os


# symbol_list = ['127008','110044','128041','128036','123006','110039','128052','113506','128038','127009','123015','123008','128043','128030','110050','123007','123020','123013','128063','123001','110052','110054']
symbol_list = ['113017','113018','113019','113020','113021','113022','113024','113025','113026','113502','113503','113504','113505','113506','113507','113508','113509','113510','113511','113512','113513','113514','113515','113516','113517','113518','113519','113520','113521','113522','113523','113524','113525','113526','113527','113528','113529','113530','113531','113532','113533','113534','113535','123001','123002','123003','123004','123005','123006','123007','123008','123009','123010','123011','123012','123013','123014','123015','123016','123017','123018','123019','123020','123021','123022','123023','123024','123025','127003','127004','127005','127006','127007','127008','127009','127010','127011','127012','127013','128010','128012','128013','128014','128015','128016','128017','128018','128019','128020','128021','128022','128023','128024','128025','128026','128027','128028','128029','128030','128032','128033','128034','128035','128036','128037','128038','128039','128040','128041','128042','128043','128044','128045','128046','128047','128048','128049','128050','128051','128052','128053','128054','128055','128056','128057','128058','128059','128060','128061','128062','128063','128064','128065','128066','128067','132004','132005','132007','132008','132009','132011','132013','132014','132015','132017','132018']
scale = ['5','30','60']

def update_cb(symbol_list, scale):
    conn, cur = connDB()
    for symbol in symbol_list:
        if symbol.startswith('12'):
            sym = 'sz' + symbol
        else:
            sym = 'sh' + symbol
        for s in scale:
            url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=' + sym + '&scale=' + s +'&ma=no&datalen=50'
            response = rq.urlopen(url, timeout=20)
            r_data = response.read().decode('utf-8', 'ignore')
            if r_data  == 'null' or len(r_data) <= 4:
                continue
            r_data = r_data.replace('[','').replace (']','').replace('{','{"').replace(':"','":"').replace('",','","').replace('},','},,').split(',,')
            for rec in r_data:
                insert_data = json.loads(rec)
                insert_sql = 'insert into data.cb_price (datetime,open,high,low,close,volume,symbol,type) VALUES(' + str(list(insert_data.values())).replace(']','').replace('[','') + ',\'' + symbol + '\',\'' + s + '\');'
                # print(insert_sql)
                try:
                    conn.cursor().execute(insert_sql)
                except Exception as e:
                    print(e)
            conn.commit()
        print(symbol + '(' + str(symbol_list.index(symbol)+1) + '/' + str(len(symbol_list)) +') is inserted into data.cb_price')
        time.sleep(3)
    connClose(conn, cur)


def update_cb_tdx():
    path = 'C:\\tdx\\T0002\\export\\'
    conn, cur = connDB()
    files = os.listdir(path)
    for filename in files:
        stockprice = open(path + filename, mode='r', encoding=None, errors=None, newline=None, closefd=True,
                          opener=None)
        content = stockprice.readlines()
        if len(content) <= 3:
            continue
        symbol = content[0][0:6]
        type = content[0].split(' ')[2][0]
        content.pop()
        for i in range(2,len(content)):
            m_data = content[i].strip().split(',')
            insert_sql = 'insert into data.cb_price (datetime,open,high,low,close,volume,symbol,type) VALUES(\''\
                         + m_data[0].replace('/','-') + ' ' + m_data[1][0:2] + ':' + m_data[1][2:] +':00\',' \
                         + str(m_data[2:7]).replace('[','').replace(']','') + ',\'' + symbol + '\',\'' + type +'\');'

            try:
                conn.cursor().execute(insert_sql)
            except Exception as e:
                print(insert_sql)
                print(e)
        conn.commit()
        print(symbol + '(' + str(files.index(filename)+1) + '/' + str(len(files)) + ') is inserted into data.cb_price')
    connClose(conn, cur)



update_cb(symbol_list,scale)
# update_cb_tdx()