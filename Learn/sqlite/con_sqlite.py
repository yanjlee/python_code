# 导入SQLite驱动:
import sqlite3
# 连接到SQLite数据库
# 数据库文件是test.db
# 如果文件不存在，会自动在当前目录创建:
conn = sqlite3.connect('test.db')
# 创建一个Cursor:
cursor = conn.cursor()
# 执行一条SQL语句，创建user表:
cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')
#<sqlite3.Cursor object at 0x10f8aa260>


# sqlite支持建立自增主键，sql语句如下：

# CREATE TABLE w_user(
# id integer primary key autoincrement,
# userename varchar(32),
# usercname varchar(32),
# userpassword varchar(32),
# userpermission varchar(32),
# userrole varchar(32),
# userdesc varchar(32)
# );

##联合主键，在建表时
# CREATE TABLE tb_test (
# bh varchar(5),
# id integer,
# ch varchar(20),
# mm varchar(20),
# primary key (id,bh));

# 继续执行一条SQL语句，插入一条记录:
cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
#<sqlite3.Cursor object at 0x10f8aa260>

# 通过rowcount获得插入的行数:
cursor.rowcount

# 关闭Cursor:
cursor.close()
# 提交事务:
conn.commit()
# 关闭Connection:
conn.close()

#--------------------
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
# 执行查询语句:
cursor.execute('select * from user where id=?', ('1',))
#<sqlite3.Cursor object at 0x10f8aa340>

#如果SQL语句带有参数，那么需要把参数按照位置传递给execute()方法，有几个?占位符就必须对应几个参数
cursor.execute('select * from user where name=? and pwd=?', ('abc', '123456'))
# 获得查询结果集:
values = cursor.fetchall()
cursor.close()
conn.close()