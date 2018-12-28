import logging as log

log.basicConfig(
    level=log.DEBUG,
    # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
    format="%(levelname)s: %(message)s")

# w.start()
# divSet = w.wset('sectorconstituent', "2018-03-12", 'sectorid=a001010100000000').Data[1]

# w.isconnected()
# w = w.wsd('600001.sh','open,close','20130707','20130909',showblank=0)

# w1 = w.wsd("090007.IB", "CLOSE", "2016-07-11", "2016-08-09", "TradingCalendar=szse;PriceAdj=f")
# log.info(w1)

# code = ['600000.SH', '600005.SH', '600004.SH']
# field = ['roe_avg', 'roa']
# w2 = w.wss(code, field, "rptDate=20121231")
# log.info(w2)

# w3 = w.wsd("600000.SH", "high", "2018-02-09", datetime.today(), "Period=W")
# log.info(w3)

# w4 = w.wsd('600001.sh','open,close','20130707','20130909',showblank=0)
#  w.wsd('600001.sh','open,close','20130707','20130909',showblank=-1);
# log.info(w4)

# w5 = w.tquery(1, logonid=1, showfields='securitycode,Profit,securityBalance')
# log.info(w5)

# w6 = w.wsi("600000.SH", "close,amt", "2018-02-26 9:00:00") # 最多三年
# log.info(w6)

# w7 = w.wst("600000.SH", "open", '20180305', datetime.now())  # tick数据, 最多7天
# log.info(w7)

# w8 = w.wss("600000.SH,000001.SZ", "eps_ttm,orps,surpluscapitalps", "rptDate=20161231")  # 一次只能取一个报告期，但可以取多个品种数据
# log.info(w8)

# w9 = w.wset("SectorConstituent", u"date=20180305;sector=全部A股")  # 取全部A 股股票代码、名称信息
# for row in w9.Data:
#     log.info(row)

# 取沪深300 指数中股票代码和权重
# w10 = w.wset("IndexConstituent","date=20130608;windcode=000300.SH;field=wind_code,i_weight")
# for row in w10.Data:
#     log.info(row)

# 取停牌信息
# w11 = w.wset("TradeSuspend","startdate=20180305;enddate=20180306;field=wind_code,sec_name,suspend_type,suspend_reason")
# for row in w11.Data:
#     log.info(row)

# #取ST 股票等风险警示股票信息
# w12 = w.wset("SectorConstituent", u"date=20180306;sector=风险警示股票;field=wind_code,sec_name")
# for row in w12.Data:
#     log.info(row)

# 条件选股 data= w.weqs(filtername,…)；

# 模拟交易
# LogonId = w.tlogon('0000', 0, ['w3184800401', 'w3184800402'], '000000', ['sh', 'cfe'])  # 同时登陆两个账号
# LogonId = w.tlogout([1, 2])

# startdate = (datetime.date.today() - datetime.timedelta(365 * 4)).strftime('%Y%m%d')
# enddate = (datetime.date.today()).strftime('%Y%m%d')
#
# i = w.wsd("I.DCE", "trade_hiscode,close", startdate, enddate, "")
# i_data = DataFrame(i.Data, index=['i_HISCODE', 'CLOSE'], columns=i.Times).T

# # 通过wset来取数据集数据
# print('\n\n' + '-----通过wset来取数据集数据,获取全部A股代码列表-----' + '\n')
# # wsetdata=w.wset('SectorConstituent','date=20160116;sectorId=a001010100000000')
# wsetdata = w.wset('SectorConstituent', u'date=20160116;sector=全部A股;field=wind_code')
# print(wsetdata)
# # a_list = wsetdata.Data[0]
# # print(a_list)
# dt = datetime.now()
#
# for j in range(0, len(wsetdata.Data[0])):
#     # 通过wsd来提取时间序列数据，比如取开高低收成交量，成交额数据
#     print("\n\n-----第 %i 次通过wsd来提取 %s 开高低收成交量数据-----\n" % (j, str(wsetdata.Data[0][j])))
#     wssdata = w.wss(str(wsetdata.Data[0][j]), 'ipo_date')
#     print(wssdata)
#     wsddata1 = w.wsd(str(wsetdata.Data[0][j]), "open,high,low,close,volume,amt", wssdata.Data[0][0], dt,
#                      "Fill=Previous")
#     if wsddata1.ErrorCode != 0:
#         continue
#     print(wsddata1)
# import arrow
# request_date = '2015-03-31'
#
# date_temp = arrow.get(request_date, 'YYYY-MM-DD').ceil("quarter").replace(quarters=-1).date()
# last_quarter = date.strftime(date_temp, '%Y-%m-%d')
# print(last_quarter)
# w.start()
from CIGRG.CIGRG001.ConnectDB import get_all_data

# end_date = datetime.strptime('2012-09-30','%Y-%m-%d')
# temp_date = arrow.get(end_date).replace(years=-5).date()
# end_date = date.strftime(end_date, '%Y-%m-%d')
# start_date = date.strftime(temp_date, '%Y-%m-%d')
# items = 'roe_ttm'
# table = 'stk_fina_calc'
# condition = ' where symbol = \'' + '000002.SZ' + '\'  and date between \'' + start_date + '\' and \'' + end_date + '\' and date like \'%-' + end_date[-5:] + '\' and roe_ttm is not null order by date asc'
# roe_data = get_all_data(items, table, condition)
# roe_list = []
# for j in roe_data:
#     roe_list.append(float(j[0]))
# roe_std = {}
# roe_std[]

requestDate = '2018-04-14'
item2 = 'pb'
table2 = 'stk_ratio'
condition2 = ' where symbol = \'' + '000001.SZ' + '\'  and date = \'' + requestDate + '\''
pb_data = get_all_data(item2, table2, condition2)