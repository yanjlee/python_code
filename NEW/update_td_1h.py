# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from ConnectDB import get_all_data, fill_data
# from string import digits
from datetime import datetime, timedelta

set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')



def InsertTdData_1h(symbol, stime, etime):
    fur_data = history(symbol=symbol, frequency='60m', start_time = stime, end_time = etime, fields='open,high,low,close,volume,bob',fill_missing='Last',adjust=1, df = 'True')
    if len(fur_data) > 0:
        for i in range(0, len(fur_data)):
            data_string = str(list(fur_data.iloc[i])).replace('[Timestamp(','(\'' + symbol + '\',' ).replace(')','').replace(']',');')
            insert_sql =  'insert into data.td_price_1h (symbol, dtime, close, high, low, open, volume) values' + data_string
            try:
                fill_data(insert_sql)
            except Exception as e:
                print(e)
                print(insert_sql)


def UpdateInfo_1h(start_time, end_time, symbol_list):
    n_days = int((datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')).days/90 + 1)
    for i in range(0,len(symbol_list)):
        stime = start_time
        for n in range(1, n_days+1):
            etime = (datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') + timedelta(days=90*n)).strftime('%Y-%m-%d %H:%M:%S')
            if etime > end_time:
                etime = end_time

            print(symbol_list[i] + ': ' + stime + ' ~ ' + etime)
            InsertTdData_1h(symbol_list[i],stime,etime)
            stime = etime
        print(symbol_list[i] + ' is updated.')


def get_time():
    items = 'max(dtime)'
    tables = 'data.td_price_1m'
    condition = ' '
    date_info = get_all_data(items, tables, condition)
    start_time = date_info[0][0].strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return(start_time,end_time)


# start, end = get_time()
symbol_list = ['SHSE.000001','SHSE.000016','SHSE.000300','SHSE.510050','SHSE.510500','SHSE.510880','SHSE.510900','SHSE.511260','SHSE.512880','SHSE.513500','SHSE.518880','SHSE.600000','SHSE.600009','SHSE.600010','SHSE.600011','SHSE.600015','SHSE.600016','SHSE.600018','SHSE.600019','SHSE.600023','SHSE.600027','SHSE.600028','SHSE.600029','SHSE.600030','SHSE.600031','SHSE.600036','SHSE.600038','SHSE.600048','SHSE.600050','SHSE.600061','SHSE.600066','SHSE.600068','SHSE.600085','SHSE.600089','SHSE.600104','SHSE.600109','SHSE.600111','SHSE.600115','SHSE.600118','SHSE.600153','SHSE.600170','SHSE.600176','SHSE.600177','SHSE.600196','SHSE.600208','SHSE.600271','SHSE.600273','SHSE.600276','SHSE.600297','SHSE.600332','SHSE.600340','SHSE.600346','SHSE.600352','SHSE.600362','SHSE.600369','SHSE.600372','SHSE.600383','SHSE.600388','SHSE.600398','SHSE.600406','SHSE.600415','SHSE.600436','SHSE.600438','SHSE.600482','SHSE.600487','SHSE.600489','SHSE.600498','SHSE.600508','SHSE.600516','SHSE.600518','SHSE.600519','SHSE.600522','SHSE.600535','SHSE.600547','SHSE.600549','SHSE.600566','SHSE.600570','SHSE.600583','SHSE.600585','SHSE.600588','SHSE.600606','SHSE.600612','SHSE.600637','SHSE.600660','SHSE.600674','SHSE.600688','SHSE.600690','SHSE.600703','SHSE.600705','SHSE.600739','SHSE.600741','SHSE.600760','SHSE.600795','SHSE.600809','SHSE.600816','SHSE.600837','SHSE.600867','SHSE.600886','SHSE.600887','SHSE.600893','SHSE.600900','SHSE.600909','SHSE.600919','SHSE.600926','SHSE.600958','SHSE.600977','SHSE.600987','SHSE.600998','SHSE.600999','SHSE.601006','SHSE.601009','SHSE.601012','SHSE.601018','SHSE.601021','SHSE.601088','SHSE.601108','SHSE.601111','SHSE.601117','SHSE.601155','SHSE.601166','SHSE.601169','SHSE.601186','SHSE.601198','SHSE.601211','SHSE.601225','SHSE.601229','SHSE.601238','SHSE.601288','SHSE.601318','SHSE.601328','SHSE.601333','SHSE.601336','SHSE.601360','SHSE.601377','SHSE.601390','SHSE.601398','SHSE.601555','SHSE.601601','SHSE.601607','SHSE.601611','SHSE.601618','SHSE.601628','SHSE.601668','SHSE.601669','SHSE.601688','SHSE.601727','SHSE.601766','SHSE.601788','SHSE.601800','SHSE.601818','SHSE.601857','SHSE.601877','SHSE.601888','SHSE.601899','SHSE.601901','SHSE.601919','SHSE.601933','SHSE.601939','SHSE.601985','SHSE.601988','SHSE.601989','SHSE.601992','SHSE.601997','SHSE.601998','SHSE.603288','SHSE.603799','SHSE.603833','SHSE.603858','SHSE.603898','SHSE.603993','SZSE.000001','SZSE.000002','SZSE.000063','SZSE.000069','SZSE.000100','SZSE.000157','SZSE.000166','SZSE.000333','SZSE.000338','SZSE.000402','SZSE.000413','SZSE.000423','SZSE.000425','SZSE.000538','SZSE.000568','SZSE.000625','SZSE.000627','SZSE.000630','SZSE.000651','SZSE.000661','SZSE.000671','SZSE.000709','SZSE.000725','SZSE.000728','SZSE.000768','SZSE.000776','SZSE.000783','SZSE.000792','SZSE.000826','SZSE.000839','SZSE.000848','SZSE.000858','SZSE.000876','SZSE.000887','SZSE.000895','SZSE.000898','SZSE.000938','SZSE.000961','SZSE.000963','SZSE.000983','SZSE.001979','SZSE.002001','SZSE.002007','SZSE.002008','SZSE.002024','SZSE.002027','SZSE.002032','SZSE.002044','SZSE.002050','SZSE.002065','SZSE.002081','SZSE.002085','SZSE.002142','SZSE.002146','SZSE.002153','SZSE.002179','SZSE.002202','SZSE.002230','SZSE.002236','SZSE.002241','SZSE.002271','SZSE.002275','SZSE.002285','SZSE.002294','SZSE.002304','SZSE.002310','SZSE.002311','SZSE.002352','SZSE.002415','SZSE.002422','SZSE.002450','SZSE.002456','SZSE.002460','SZSE.002466','SZSE.002475','SZSE.002493','SZSE.002508','SZSE.002555','SZSE.002558','SZSE.002572','SZSE.002594','SZSE.002601','SZSE.002602','SZSE.002624','SZSE.002673','SZSE.002714','SZSE.002736','SZSE.002773','SZSE.002797','SZSE.002833','SZSE.159901','SZSE.159915','SZSE.159919','SZSE.300003','SZSE.300015','SZSE.300017','SZSE.300024','SZSE.300033','SZSE.300059','SZSE.300070','SZSE.300072','SZSE.300122','SZSE.300124','SZSE.300136','SZSE.300142','SZSE.300144','SZSE.300251','SZSE.300296','SZSE.300408','SZSE.300433','SZSE.399001','SZSE.399905']
start = '2014-01-01 09:28:00'
end = '2015-01-01 15:31:00'
# UpdateInfo(start, end,symbol_list)
UpdateInfo_1h(start, end,symbol_list)