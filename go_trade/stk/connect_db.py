# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1.0.0
# -=-=-=-=-=-=-=-=-=-=-=
import sqlite3


def connDB():  # 连接数据库函数
    conn = sqlite3.connect('C:/codes/easytrader/tsdata.db')
    cur = conn.cursor();
    return (conn, cur);

def connClose(conn, cur):  # 关闭所有连接
    cur.close();
    conn.commit();
    conn.close();

def fill_data(query_sql):
    conn, cur = connDB()
    try:
        cur.execute(query_sql)
    except Exception as e:
        print(e)
        print(query_sql)
        # pass
    connClose(conn, cur)


def get_data(items, table, symbol, startDate, endDate):
    conn, cur = connDB()
    query_sql = 'select ' + items + ' from ' + table + ' where symbol in ('+ str(symbol).replace('[','').replace(']','') + ') and date between \'' + startDate + '\' and \'' + endDate + '\' order by symbol, date'
    # print(query_sql)
    try:
        cur.execute(query_sql)
        db_data = cur.fetchall()
    except Exception as e:
        print(e)
        print(query_sql)
    connClose(conn, cur)
    return (db_data)


def get_all_data(items, table, condition):
    conn, cur = connDB()
    query_sql = 'select ' + items + ' from ' + table + ' ' + condition
    try:
        cur.execute(query_sql)
        db_data = cur.fetchall()
    except Exception as e:
        print(e)
        db_data =[]
    connClose(conn, cur)
    return (db_data)