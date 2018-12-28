# -*- coding:utf-8 -*-
# Author:OpenAPISupport@wind.com.cn
# Editdate:2017-11-15

from CIGRG.WindPy import *
import MySQLdb
import datetime

w.start()

#连接数据库
conn = MySQLdb.connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='123456',
    db='wind',
    )
cur = conn.cursor()

#创建数据库表
cur.execute("""
CREATE TABLE stockprice(
    secid VARCHAR(20) NOT NULL,
    tradedate VARCHAR(50),
    openprice VARCHAR(50),
    highprice VARCHAR(50),
    lowprice VARCHAR(50),
    closeprice VARCHAR(50))
""");

#通过wset提取板块成分数据集
print('\n\n'+'-----通过wset来取数据集数据,获取沪深300代码列表-----'+'\n')
todayDate=datetime.datetime.strftime(datetime.date.today(),"%Y%m%d")
wsetdata=w.wset('SectorConstituent','date='+todayDate+';sectorId=1000000090000000;field=wind_code')
print(wsetdata)

for j in range(len(wsetdata.Data[0])):
    #通过wsd提取沪深300高开低收数据
    print "\n\n-----第 %i 次通过wsd来提取 %s 开高低收成交量数据-----\n" %(j,str(wsetdata.Data[0][j]))

    wssdata=w.wss(str(wsetdata.Data[0][j]),'ipo_date')
    wsddata=w.wsd(str(wsetdata.Data[0][j]), "open,high,low,close", wssdata.Data[0][0], todayDate, "Fill=Previous")

    if wsddata.ErrorCode!=0:
        continue
    print wsddata
    for i in range(len(wsddata.Data[0])):
        sqllist=[]
        sqltuple=()
        sqllist.append(str(wsetdata.Data[0][j]))
        if len(wsddata.Times)>1:
            sqllist.append(wsddata.Times[i].strftime('%Y%m%d'))
        for k in range(len(wsddata.Fields)):
            sqllist.append(str(wsddata.Data[k][i]))
        sqltuple=tuple(sqllist)
        cur.execute("insert into stockprice VALUES('%s','%s','%s','%s','%s','%s')"%sqltuple)
    conn.commit()
conn.close() 



