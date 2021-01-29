from DatasetRenew import RenewData
from Signal import getRSI,MA,KDJ
import Calculation
from Optimization import optimize
import pandas as pd
import numpy as np


Dataset, Benchmark = RenewData(NeedtoRenew = False)

weight = getRSI(Dataset)#.add(MA(Dataset['Adj Close'], 5, 10), fill_value = 0)

print (weight.sort_values(ascending = False))

Beta = Calculation.get_beta(pd.DataFrame(Benchmark['Adj Close']), Dataset['Adj Close'], weight)

targetbeta = -0.5

weights, variance = optimize(Dataset, weight, Beta, targetbeta)

while np.abs(variance) > 0.1:

	targetbeta = float(input("The variance is not satisfied, please re-enter a targetbeta: "))

	weights, variance = optimize(Dataset, weight, Beta, targetbeta)

Position = Calculation.get_position(2000000, Dataset['Adj Close'][weights.index.values], weights, Beta, ratio = 0.01)

MyPort = pd.read_csv('My_Portfolio/OpenPosition_3_14_2019.csv', header = 0 , index_col = 0).Quantity

reb = Calculation.rebalance(Position, MyPort)
