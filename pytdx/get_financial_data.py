from pytdx.crawler.history_financial_crawler import HistoryFinancialListCrawler
import pandas as pd

## get financial package list
# crawler = HistoryFinancialListCrawler()
# list_data = crawler.fetch_and_parse()#
# print(pd.DataFrame(data=list_data))

from pytdx.crawler.base_crawler import demo_reporthook
from pytdx.crawler.history_financial_crawler import HistoryFinancialCrawler
from pytdx.reader import HistoryFinancialReader

## download financial packages
# datacrawler = HistoryFinancialCrawler()
# pd.set_option('display.max_columns', None)
# result = datacrawler.fetch_and_parse(reporthook=demo_reporthook, filename='gpcw20180930.zip', path_to_download="C:/codes/pytdx/tmp/tmpfile.zip")
# print(datacrawler.to_df(data=result))


# read data file
print(HistoryFinancialReader().get_df('C:/codes/pytdx/tmp/tmpfile.zip'))
# print(HistoryFinancialReader().get_df('/tmp/gpcw20170930.dat'))

# write to csv
financial_data  = HistoryFinancialReader().get_df('C:/codes/pytdx/tmp/tmpfile.zip')
financial_data.to_csv('C:/codes/pytdx/tmp/financial_data.csv')

##  https://github.com/QUANTAXIS/QUANTAXIS/blob/master/QUANTAXIS/QAData/financial_mean.py
