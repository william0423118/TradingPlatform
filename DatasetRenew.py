import pandas_datareader as pdr
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
from tqdm import tqdm
import pandas as pd
import numpy as np


def RenewData(NeedtoRenew = True):
	if NeedtoRenew:
		df = pd.read_excel("Securities List short.xlsx")
		Universe = np.array(df['Ticker'])

		Dataset = pd.read_csv('dataset/Dataset.csv', header = [0, 1], index_col = 0)
		Benchmark = pd.read_csv('dataset/Benchmark.csv', header = 0, index_col = 0)

		LastDay = Benchmark.index[-1]
		LastDay1 = (datetime.strptime(LastDay, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
		Today = datetime.now().strftime('%Y-%m-%d')

		TempDataset = pdr.get_data_yahoo(Universe[0:1], LastDay1, Today , interval='d')
		for i in tqdm(range(1, Universe.size)):
		    try:
		        TempDataset = TempDataset.join(pdr.get_data_yahoo(Universe[i:i+1], LastDay1, Today ,
		                                                  interval='d'), how = 'left')
		    except:
		        i = i + 1
		        print ('Fail to download' + Universe[i])

		TempBM = pd.DataFrame(pdr.get_data_yahoo('SPY', LastDay1, Today , interval='d'))

		DatasetNew = pd.concat([Dataset, TempDataset])
		BenchmarkNew = pd.concat([Benchmark, TempBM])

		DatasetNew = DatasetNew.reindex(index = pd.to_datetime(DatasetNew.index))
		BenchmarkNew = BenchmarkNew.reindex(index = pd.to_datetime(BenchmarkNew.index))

		DatasetNew = DatasetNew[~DatasetNew.index.duplicated(keep='first')]
		BenchmarkNew = BenchmarkNew[~BenchmarkNew.index.duplicated(keep='first')]

		DatasetNew.to_csv('dataset/Dataset.csv')
		BenchmarkNew.to_csv('dataset/Benchmark.csv')

		return DatasetNew, BenchmarkNew
	else:
		df = pd.read_excel("Securities List short.xlsx")
		Universe = np.array(df['Ticker'])

		Dataset = pd.read_csv('dataset/Dataset.csv', header = [0, 1], index_col = 0)
		Benchmark = pd.read_csv('dataset/Benchmark.csv', header = 0, index_col = 0)
		return 	Dataset, Benchmark

if __name__ == "__main__":
	Dataset, Benchmark = RenewData(NeedtoRenew = True)
	print ('Dataset Renew finished, to the date: ', Dataset.index[-1])