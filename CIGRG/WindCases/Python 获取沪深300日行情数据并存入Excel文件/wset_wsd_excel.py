# -*- coding:utf-8 -*-
# Author:OpenAPISupport@wind.com.cn  
# Editdate:2017-09-06

from CIGRG.WindPy import *
w.start()

import os
import datetime  #datetime
import xlwt  #excel

# 取当前沪深300成份股2016年至今的日行情(2016年后上市的品种则取上市日至今),并将数据存入EXCEL
# 命令如何写可以用命令生成器来辅助完成


# 通过wset取当前沪深300成份股
print('\n'+'-----通过wset来获取沪深300代码列表-----'+'\n')
stockSector=w.wset("sectorconstituent","date="+datetime.date.today().strftime('%Y-%m-%d')+";sectorid=1000000090000000") 
print(stockSector)


#建立excel文件, 并设置格式
f=xlwt.Workbook()

borders = xlwt.Borders() # Create Borders
borders.left = 1
borders.right = 1
borders.top = 1
borders.bottom = 1
borders.left_colour = 0x40
borders.right_colour = 0x40
borders.top_colour = 0x40
borders.bottom_colour = 0x40

alignment = xlwt.Alignment() # Create Alignment
alignment.horz = xlwt.Alignment.HORZ_LEFT
alignment.vert = xlwt.Alignment.VERT_CENTER 

style = xlwt.XFStyle() # Create Style
style.borders = borders # Add Borders to Style
style.alignment = alignment # Add Alignment to Style

#数据录入excel
for k in range(len(stockSector.Data[1])):   
    ipoDate=w.wss(stockSector.Data[1][k],'ipo_date').Data[0][0].strftime('%Y-%m-%d')
    if ipoDate>"2016-01-01":
        beginDate=ipoDate
    else:
        beginDate="2016-01-01"
    
    endDate=(datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    dailyQuota=w.wsd(stockSector.Data[1][k], "open,high,low,close", beginDate, endDate, "Fill=Previous")

    sheet = f.add_sheet(stockSector.Data[1][k],cell_overwrite_ok=True) #创建sheet
    sheetColName=["date","open","high","low","close"]
    sheetRowName=dailyQuota.Times

    print('\n'+'-----开始录入%s开高低收数据-----\n' %str(stockSector.Data[1][k]))
    for j in range(len(sheetColName)):       
        sheet.col(j).width=256*12
        for i in range(len(sheetRowName)+1):
            if j==0 and i==0:
                sheet.write(i, j, sheetColName[j], style)
            elif i==0:
                sheet.write(i, j, sheetColName[j], style)
            elif j==0:
                sheet.write(i, j, sheetRowName[i-1].strftime('%Y-%m-%d'), style)                
            else:
                sheet.write(i, j, dailyQuota.Data[j-1][i-1], style)             

f.save(os.getcwd()+'\\statistics.xls') #保存文件
print('\n'+'-----沪深300成分日行情写入EXCEL完成-----'+'\n')

os.startfile(os.getcwd()+'\\statistics.xls')     

w.stop()
