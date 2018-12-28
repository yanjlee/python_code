import pandas as pd
#import math
#import matplotlib.pyplot as plt

symbol_list = ['SZSE.000002','SZSE.000333','SZSE.002456','SHSE.601318','SHSE.600508','SHSE.600660','SHSE.603288']
start_list = ['2014-01-01','2014-12-31','2015-12-30','2016-12-28','2017-12-27']
rs_list =[ 's','f']


for rs in rs_list:
	statMatrx = pd.DataFrame()
	for sy in symbol_list:
		for st in start_list:
			queryStr = 'start==\'' + st + '\'&symbol==\'' + sy + '\''
			test = ret.query(queryStr)
			print(test)
			test['efc'] = (test['return']-1) / - test.mdd
			test2 = test.groupby(rs)
			test3 =test2.mean()
			test3.reset_index(rs)
			statMatrx=statMatrx.append(test3)

	statMatrx.to_csv('test_' + rs + '.csv')

	test4 = statMatrx.groupby(rs)
	test5 = test4.mean()
	test5.to_csv('calc_' +  rs +'_mean.csv')
	test6 = test4.median()
	test6.to_csv('calc_' +  rs +'_median.csv')

