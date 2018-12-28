from pytdx.crawler.history_financial_crawler import HistoryFinancialListCrawler, HistoryFinancialCrawler
from pytdx.reader import HistoryFinancialReader
from pytdx.crawler.base_crawler import demo_reporthook
from ConnectDB import connDB, connClose, get_data, get_all_data
import csv
import pandas as pd
import os

# Doanload all historical data from 163 and parse to csv

path ='C:/temp/finance/'

files = os.listdir(path)
crawler = HistoryFinancialListCrawler()
list_data = crawler.fetch_and_parse()
file_name = []
for i in list_data:
    file_name.append(i['filename'])

for name in file_name[-2:]:
    if name in files:
        continue
    datacrawler = HistoryFinancialCrawler()
    pd.set_option('display.max_columns', None)
    download_target = path + name
    csv_name = download_target.replace('.zip','.csv')
    result = datacrawler.fetch_and_parse(reporthook=demo_reporthook, filename=name, path_to_download=download_target)
    datacrawler.to_df(data=result).round(3).drop(['col190','col191','col192','col283','col284','col285', 'col286'], axis=1).drop_duplicates(subset=None, keep='first', inplace=False).to_csv(csv_name)

# for name in files:
#     target = path + name
#     csv_name = target.replace('.dat','.csv')
#     HistoryFinancialReader().get_df(target).round(3).drop(['col190','col191','col192','col283','col284','col285', 'col286'], axis=1).drop_duplicates(subset=None, keep='first', inplace=False).to_csv(csv_name)