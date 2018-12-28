# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=
import logging as log
import pandas as pd
# import datetime, time
# from datetime import timedelta, datetime
import os
import urllib.request
import tushare as ts
from ConnectDB import connDB, connClose, get_data, get_all_data
# import pymysql
import csv

path ='C:/temp/financial/' #Stock 下载、处理和导入数据路径


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
    conn, cur = connDB()
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
    connClose(conn, cur)

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

            for j in range(0, data_content.index.size):
                # finance_value = []
                finance_value = list(data_content.loc[j])
                finance_value = ['NULL' if x == '--' else x for x in finance_value]
                finance_value.insert(0, filename.replace('.csv', ''))
                insert_sql = 'insert into data.stk_finance values (' + str(finance_value).replace('[', '').replace(']', '').replace('\'NULL\'', 'default') + ');'

                conn, cur = connDB()
                try:
                    cur.execute(insert_sql)
                except Exception as e:
                    print(e)
                connClose(conn, cur)

        log.info(filename.replace('.csv', '') + 'is loaded.')

download_financial_data()
load_financial_data()