# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import pandas as pd
import os
import urllib.request
from ConnectDB import get_all_data, fill_data
import csv
from datetime import datetime as dt, timedelta


# 设置token
set_token('73f0f9b75e0ffe88aa3f04caa8d0d9be22ceda2d')

path ='C:/temp/financial/' #下载、处理和导入数据路径

def download(symbol_list, file_list):
    for k in range(0, len(symbol_list)):
        if symbol_list[k] in file_list:
            continue
        symbol = symbol_list[k].strip().replace('.SZ', '').replace('.SH', '')
        url = 'http://quotes.money.163.com/service/zycwzb_' + symbol + '.html'

        local = path + symbol_list[k].strip() + '.csv'
        try:
            urllib.request.urlretrieve(url, local)
            print(symbol_list[k].strip() + ' is downloaded.')
        except Exception as e:
            print(e)

def file_name():
    files = os.listdir(path)
    file_list = []
    for i in files:
        file_list.append(i.replace('.csv',''))
    return(file_list)

def download_financial_data():
    items = 'symbol'
    table = 'stk_info'
    condition = ' order by symbol'
    symbol_list = []
    symbol_data = get_all_data(items, table, condition)
    for i in symbol_data:
        symbol_list.append(i[0])
    file_list = []
    while len(symbol_list) != len(file_list):
        file_list = file_name()
        download(symbol_list, file_list)

def load_financial_data():
    for filename in os.listdir(path):
        with open(path + filename, newline='') as csvfile:
            reader_csv = csv.reader(csvfile)
            csv_content = {}
            for i in reader_csv:
                if i[0] != '\t\t':
                    csv_key = i[0]
                    csv_value = i[1:]
                    csv_value.pop()
                    csv_content[csv_key] = csv_value

            data_content = pd.DataFrame(csv_content, columns=['报告日期', '基本每股收益(元)', '每股净资产(元)', '每股经营活动产生的现金流量净额(元)', '净资产收益率加权(%)', '主营业务收入(万元)', '主营业务利润(万元)', '营业利润(万元)', '投资收益(万元)', '营业外收支净额(万元)', '利润总额(万元)', '净利润(万元)', '净利润(扣除非经常性损益后)(万元)', '经营活动产生的现金流量净额(万元)', '现金及现金等价物净增加额(万元)', '总资产(万元)', '流动资产(万元)', '总负债(万元)', '流动负债(万元)', '股东权益不含少数股东权益(万元)'])

            for j in range(0,2):# data_content.index.size):

                finance_value = list(data_content.loc[j])
                finance_value = ['NULL' if x == '--' else x for x in finance_value]
                finance_value.insert(0, filename.replace('.csv', ''))
                insert_sql = 'insert into data.stk_finance values (' + str(finance_value).replace('[', '').replace(']', '').replace('\'NULL\'', 'default') + ');'
                try:
                    fill_data(insert_sql)
                except Exception as e:
                    print(e)
        print(filename.replace('.csv', '') + 'is loaded.')


def get_symbols(table):
    items = 'symbol'
    condition = ' group by symbol order by symbol'
    symbol_list = []
    symbol_data = get_all_data(items, table, condition)
    for item in symbol_data:
        symbol_list.append(item[0])
    return(symbol_list)


def update_eps_roe(symbol_list, df):
    for symbol in symbol_list:
        items = 'date, eps, roe '
        table = 'stk_finance'
        condition = ' where symbol = \'' + symbol + '\' and date in ' + str(quartly_date).replace('[','(').replace(']',')') + ' order by date asc '
        symbol_data = get_all_data(items, table, condition)
        e_data = []
        for i in symbol_data:
            e_data.append([i[0].strftime('%Y-%m-%d'),i[1],i[2]])
        if len(e_data) == 0:
            continue
        df_e = pd.DataFrame(e_data,columns=['date','eps','roe'])
        df_e = df_e.set_index('date')
        df_e = df.join(df_e)

        ## eps_ttm & roe_ttm
        ttm = []
        for i in range(5, len(df_e)):
            temp = [df_e.index[i]]
            for j in ['eps','roe']:
                if i % 4 == 1:
                    if df_e[j][i] == None or df_e[j][i-1] == None or df_e[j][i-4] == None or pd.isnull(df_e[j][i]) or pd.isnull(df_e[j][i-1]) or pd.isnull(df_e[j][i-4]):
                        temp_1 = 'NULL'
                    else:
                        temp_1 = round(df_e[j][i] + df_e[j][i-1] - df_e[j][i-4],3)
                elif i % 4 == 2:
                    if df_e[j][i] == None or df_e[j][i-2] == None or df_e[j][i-4] == None or pd.isnull(df_e[j][i]) or pd.isnull(df_e[j][i-2]) or pd.isnull(df_e[j][i-4]):
                        temp_1 = 'NULL'
                    else:
                        temp_1 = round(df_e[j][i] + df_e[j][i-2] - df_e[j][i-4],3)
                elif i % 4 == 3:
                    if df_e[j][i] == None or df_e[j][i-3] == None or df_e[j][i-4] == None or pd.isnull(df_e[j][i]) or pd.isnull(df_e[j][i-3]) or pd.isnull(df_e[j][i-4]):
                        temp_1 = 'NULL'
                    else:
                        temp_1 = round(df_e[j][i] + df_e[j][i-3] - df_e[j][i-4],3)
                else:
                    if df_e[j][i] == None or pd.isnull(df_e[j][i]):
                        temp_1 = 'NULL'
                    else:
                        temp_1 = round(df_e[j][i],3)
                temp.append(temp_1)
            ttm.append(temp)

        for t in ttm:
            if t[0] > '2017-12-31':
                insert_str = 'INSERT INTO data.stk_fina_calc(symbol, date, eps_ttm, roe_ttm) values(\'' + symbol + '\',\''  + str(t[0]) + '\',' + str(t[1]) + ',' + str(t[2]) + ');'
                try:
                    fill_data(insert_str)
                except Exception as e:
                    print(e)
                    print(insert_str)

            if t[1] != 'NULL':
                update_eps = 'UPDATE data.stk_fina_calc SET eps_ttm = ' + str(t[1]) + ' where symbol = \'' + symbol + '\' and date = \'' + t[0] + '\';'
                try:
                    fill_data(update_eps)
                except Exception as e:
                    print(e)
                    print(update_eps)

            if t[2] != 'NULL':
                update_roe = 'UPDATE data.stk_fina_calc SET roe_ttm = ' + str(t[2]) + ' where symbol = \'' + symbol + '\' and date = \'' + t[0] + '\';'
                try:
                    fill_data(update_roe)
                except Exception as e:
                    print(e)
                    print(update_roe)

        print(symbol + ': eps_ttm & roe_ttm is updated.')



def get_df(quartly_date):
    df = pd.DataFrame(quartly_date,columns=['date'])
    df = df.sort_values('date')
    df = df.set_index('date')
    return(df)

def update_roic(symbol_list, df, start_date, end_date): ## rpt_date & roic_ttm
    for symbol in symbol_list:
        if symbol.startswith('6'):
            sym = 'SHSE.' + symbol.replace('.SH', '')
        else:
            sym = 'SZSE.' + symbol.replace('.SZ','')
        roic = get_fundamentals(table='deriv_finance_indicator', symbols=sym, start_date=start_date, end_date=end_date,fields='ROIC')#,df = 'True')
        if len(roic) == 0:
            continue
        df_r = pd.DataFrame(list(roic))
        df_r = df_r.set_index('end_date')
        df_r = df.join(df_r)
        # print(df_r)

        roic_ttm = []
        for i in range(5, len(df_r)):
            if 'ROIC' not in list(df_r.columns):
                temp = 'NULL'
            elif i % 4 == 1:
                if df_r.ROIC[i] == None or df_r.ROIC[i-1] == None or df_r.ROIC[i-4] == None or pd.isnull(df_r.ROIC[i]) or pd.isnull(df_r.ROIC[i-1]) or pd.isnull(df_r.ROIC[i-4]):
                    temp = 'NULL'
                else:
                    temp = round(df_r.ROIC[i] + df_r.ROIC[i-1] - df_r.ROIC[i-4],3)
            elif i % 4 == 2:
                if df_r.ROIC[i] == None or df_r.ROIC[i-2] == None or df_r.ROIC[i-4] == None or pd.isnull(df_r.ROIC[i]) or pd.isnull(df_r.ROIC[i-2]) or pd.isnull(df_r.ROIC[i-4]):
                    temp = 'NULL'
                else:
                    temp = round(df_r.ROIC[i] + df_r.ROIC[i-2] - df_r.ROIC[i-4],3)
            elif i % 4 == 3:
                if df_r.ROIC[i] == None or df_r.ROIC[i-3] == None or df_r.ROIC[i-4] == None or pd.isnull(df_r.ROIC[i]) or pd.isnull(df_r.ROIC[i-3]) or pd.isnull(df_r.ROIC[i-4]):
                    temp = 'NULL'
                else:
                    temp = round(df_r.ROIC[i] + df_r.ROIC[i-3] - df_r.ROIC[i-4],3)
            else:
                if df_r.ROIC[i] == None or pd.isnull(df_r.ROIC[i]):
                    temp = 'NULL'
                else:
                    temp = round(df_r.ROIC[i],3)

            if pd.isna(df_r.pub_date[i]):
                pub_date = 'NULL'
            else:
                pub_date = df_r.pub_date[i].strftime('%Y-%m-%d')

            roic_ttm.append([df_r.index[i].strftime('%Y-%m-%d'),pub_date,temp])

        for t in roic_ttm:
            # if t[0] > '2017-12-31':
            #     insert_str = 'INSERT INTO data.stk_fina_calc(symbol, date, rpt_date, roic_ttm) values(\'' + symbol + '\',\'' + t[0] + '\',\'' + t[1] + '\',' + str(t[2]) + ');'
            #     try:
            #         fill_data(insert_str)
            #     except Exception as e:
            #         print(e)
            #         print(insert_str)

            if t[1] != 'NULL':
                update_rpt_date = 'UPDATE data.stk_fina_calc SET rpt_date =\'' + t[1] + '\' where symbol = \'' + symbol + '\' and date = \'' + t[0] + '\';'
                try:
                    fill_data(update_rpt_date)
                except Exception as e:
                    print(e)
                    print(update_rpt_date)

            if t[2] != 'NULL':
                update_roic = 'UPDATE data.stk_fina_calc SET roic_ttm = ' + str(t[2]) + ' where symbol = \'' + symbol + '\' and date = \'' + t[0] + '\';'
                try:
                    fill_data(update_roic)
                except Exception as e:
                    print(e)
                    print(update_roic)

        print(symbol + ': rpt_date & roic_ttm is updated.')

def get_all_gm(symbol, s_time):
    df = pd.DataFrame()
    n = int((dt.now() - dt.strptime(s_time, '%Y-%m-%d')).days/365.24) + 1
    for i in range(0, n):
        start_date = (dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * i).strftime('%Y-%m-%d')
        end_date = max(dt.now().date().strftime('%Y-%m-%d'), (dt.strptime(s_time, '%Y-%m-%d') + timedelta(weeks=52) * (i+1)).strftime('%Y-%m-%d'))
        df_dy = get_fundamentals(table='trading_derivative_indicator', symbols=symbol, start_date=start_date,end_date=end_date, fields='DY', df='True')
        df = pd.concat([df,df_dy], axis=0)
        if len(df) == 0:
            continue
        df = df.drop_duplicates()
    return(df)


def update_div_yield(symbol_list, start_date, end_date):
    for symbol in symbol_list:
        if symbol.startswith('6'):
            sym = 'SHSE.' + symbol.replace('.SH', '')
        else:
            sym = 'SZSE.' + symbol.replace('.SZ', '')

        items = 'rpt_date as date'
        table = 'stk_fina_calc'
        condition = ' where symbol = \'' + symbol + '\' and rpt_date between \'' + start_date + '\' and \'' + end_date + '\' and rpt_date is not null order by date asc'
        r_data = get_all_data(items, table, condition)
        rpt_date = pd.DataFrame(list(r_data), columns=['rpt'])

        dy_data = get_all_gm(sym,start_date)
        if len(dy_data) == 0 or 'DY' not in list(dy_data.columns):
            continue
        dy_data.drop(['end_date', 'symbol'], axis=1, inplace=True)
        df = dy_data.set_index('pub_date')
        begin_date = start_date
        dy = 'NULL'
        dy_list = []
        for i in range(0, len(rpt_date)):
            df_dy = df[begin_date:rpt_date.rpt[i]]
            for j in range(0, len(df_dy)):
                if pd.isna(df_dy.DY[j]):
                    # dy = 'NULL'
                    continue
                else:
                    dy = round(df_dy.DY[j], 3)
            dy_list.append([rpt_date.rpt[i], dy])
            begin_date = rpt_date.rpt[i]

        for k in dy_list:
            update_dy = 'UPDATE data.stk_fina_calc SET div_yield = ' + str(k[1]) + ' where symbol = \'' + symbol + '\' and rpt_date = \'' + k[0].strftime('%Y-%m-%d') + '\';'
            try:
                fill_data(update_dy)
            except Exception as e:
                print(e)
                print(update_dy)
        print(symbol + ': div_yield is updated.')

download_financial_data()
load_financial_data()
# quartly_date = ['2019-03-31','2018-12-31','2018-09-30','2018-06-30','2018-03-31','2017-12-31','2017-09-30','2017-06-30','2017-03-31','2016-12-31','2016-09-30','2016-06-30','2016-03-31','2015-12-31','2015-09-30','2015-06-30','2015-03-31','2014-12-31','2014-09-30','2014-06-30','2014-03-31','2013-12-31','2013-09-30','2013-06-30','2013-03-31','2012-12-31','2012-09-30','2012-06-30','2012-03-31','2011-12-31','2011-09-30','2011-06-30','2011-03-31','2010-12-31','2010-09-30','2010-06-30','2010-03-31','2009-12-31']
quartly_date = ['2019-03-31','2018-12-31','2018-09-30','2018-06-30','2018-03-31']
start_date = quartly_date[-1]
end_date = quartly_date[0]
symbol_list = get_symbols('stk_finance')
df = get_df(quartly_date)
update_eps_roe(symbol_list, df)

update_roic(symbol_list, df,start_date, end_date)
update_div_yield(symbol_list, start_date, dt.now().date().strftime('%Y-%m-%d'))