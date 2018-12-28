# coding=UTF-8

import logging as log
import csv

# BASE_DIR = os.path.dirname(__file__)
# log.basicConfig(
#     level=log.DEBUG,
#     # format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
#     format="%(levelname)s: %(message)s"
# )

FILE = 'c:/Temp/zc_jm_data.csv'  # 原始数据
Out_File = 'c:/Temp/Test.csv'    # 输出数据

# 读取CSV文件，生成List
with open(FILE) as csv_file:
    # log.info(csv_file)
    open_file = csv.reader(csv_file)
    file_content = []
    for row in open_file:
        file_content.append(row)

# 循环，将不一致数据置为NULL
for row_number_1 in range(1, len(file_content)-1):
    for row_number_2 in range(1, len(file_content) - 1):
        if file_content[row_number_1][1] == file_content[row_number_2+1][1] and file_content[row_number_1][2] != 'NULL':
            if file_content[row_number_1][2] != file_content[row_number_2+1][2]:
                file_content[row_number_2+1][2] = 'NULL'
        if file_content[row_number_1][1] != file_content[row_number_2+1][1] and file_content[row_number_1][2] != 'NULL':
            if file_content[row_number_1][2] == file_content[row_number_2+1][2]:
                file_content[row_number_2+1][2] = 'NULL'

# 循环，将NULL赋值
for row_number_1 in range(1, len(file_content)-1):
    for row_number_2 in range(1, len(file_content) - 1):
        if file_content[row_number_1][1] == file_content[row_number_2][1] and file_content[row_number_1][2] != 'NULL' and file_content[row_number_2][2] == 'NULL':
            file_content[row_number_2][2] = file_content[row_number_1][2]

# 写入新CSV文件
out = open(Out_File, 'w', newline='')
csv_writer = csv.writer(out)
csv_writer.writerows(file_content)
