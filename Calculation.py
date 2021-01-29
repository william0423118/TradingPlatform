import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_beta(Benchmark, data, Factor):

    data = data.iloc[-1000:,:]
    Benchmark = Benchmark.iloc[-1000:,:]

    matched = Benchmark.join(data, how = 'inner')
    Return = np.log(matched / matched.shift(1))
    Corr = Return.corr().iloc[0, :]
    Cov = Return.cov().iloc[0, :]
    #print(Cov)
    Var = Cov[0]
    Beta = Cov/Var
    Beta = Beta[1:]
    Beta = Beta[Factor.index]
    return Beta

def get_position(Money, data, weights, beta, ratio = 0.03):
    price = data.iloc[-1,:]
    Position = round(Money * weights / price * (1 - ratio))
    value = (Position* price)
    print ("Long position: ", value[value>0].sum())
    print ("Short position: ", value[value<0].sum())
    print ('Market Neutral1:', (beta * weights).sum())
    print ('Market Neutral2:', (beta * value/Money).sum())
    print ('Dollar Neutral(Variance): ', (value[value>0].sum()
                                          +value[value<0].sum())/value[value>0].sum())
    return Position

def rebalance(Posit, MyPortfolio):
    Now = datetime.now()
    tod = Now.strftime('%m_%d_%Y')
    a = pd.concat([Posit, MyPortfolio], axis = 1).fillna(0)
    a['new'] = a.iloc[:,0] - a.Quantity
    a = a.rename(columns={0: "NewPosition", "Quantity": "OldPosition",'new':"OrderPlace_diff"})
    a.to_csv('position/' + tod + 'Diff' + '.csv')