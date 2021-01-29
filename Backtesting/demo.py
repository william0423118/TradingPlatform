from DB_interface.DataReader import dataReader
from Engine.engine import Market
import numpy as np
import pandas as pd
import os
import sys
sys.path.append(os.getcwd())



def scale(data):
    data = data.dropna()
    ret = data - np.mean(data)
    ret = 2*ret/np.sum(np.abs(ret))
    return ret

StartDate =  '2017-11-02'
EndData = '2019-02-28'


mkt = Market(start_date=StartDate,
             end_date=EndData,
             cash=1000000)


def Momentum(close, num): #return 2%
    close = close[::5]
    Alpha =  close.iloc[-1,:]/close.iloc[-num,:] - 1
    OrderAlpha = Alpha.sort_values().dropna()
    #print (pd.concat(([OrderAlpha[0:50], OrderAlpha[-50:]])))
    return scale(pd.concat(([OrderAlpha[0:50], OrderAlpha[-50:]])))

def RSI(close): #11%
    # wilder's RSI
    close = close[::5]
    period=14
    delta = close.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    #EMA or EWMA
    #Using zeros is not that meaningful, probably
    rUp = up.ewm(com=period - 1,  adjust=False).mean()
    rDown = down.ewm(com=period - 1, adjust=False).mean().abs()

    rsi = 100- 100 / (1 + rUp / rDown)
    rsi = 100 - rsi
    rsi_sorted = rsi.iloc[-1,:].sort_values().dropna()
    RSI = pd.concat([rsi_sorted[0:50], rsi_sorted[-50:]])
    return scale(RSI)

def KDJ(Close, High, Low, nDay):
    Close = Close[::5]
    def getRSV(Close, Low, High, nDay):
        Cn = Close.iloc[-1,:]
        Ln = np.min(Low.iloc[-nDay:,:])
        Hn = np.max(High.iloc[-nDay:,:])
        RSV = (Cn - Ln)/(Hn -Ln) *100
        return RSV
    row, col = Close.shape
    K = Close.copy()
    D = Close.copy()
    K.iloc[nDay,:]= 50
    D.iloc[nDay,:] = 50
    for i in range(nDay+1, row):
        RSV = getRSV(Close.iloc[i-nDay:i,:], Low.iloc[i-nDay:i,:], High.iloc[i-nDay:i,:], nDay)
        K.iloc[i,:] = 2/3 * K.iloc[i-1,:] + 1/3 * RSV
        D.iloc[i,:] = 2/2 *K.iloc[i-1,:] + 1/3 * K.iloc[i,:]
    kdj = (D.iloc[-1, :] - K.iloc[-1,:]).sort_values().dropna()
    return scale(pd.concat([kdj[0:50], kdj[-50:]]))

def MA(Close,short, long):
    Close = Close[::5]
    Short = Close.iloc[-short:,:].mean()
    Long = Close.iloc[-long:,:].mean()
    sig = (Short - Long).sort_values().dropna()
    return scale(pd.concat([sig[0:50], sig[-50:]]))

dr = dataReader()
dr.set_date(StartDate)
i = 0
while True:
    i = i + 1
    close = dr.get('Close', 100)
    high = dr.get('High', 100)
    low = dr.get('Low', 100)
    #print (low)
    #print(mkt.today)

    if i % 10== 0:
        Alpha =  -Momentum(close, 5) #2%
        #Alpha = -RSI(close.iloc[:-1,:]) #11.8%
        #Alpha = -KDJ(close, high, low, nDay = 14) # -Momentum(close, 5)#7% -7%
        #Alpha = MA(close, 10, 20)#-RSI(close.iloc[:-1,:])#22% 7%
        Alpha = scale(Alpha)
        TodayPrice = close.iloc[-1,:].dropna()[Alpha.index]
        tmp =mkt.portfolio_account['portfolio_value'] * 0.95 * Alpha /(TodayPrice)
        value = mkt.portfolio_account['portfolio_value'] * 0.95 * Alpha
        tmp = pd.DataFrame(tmp)

        print(mkt.today)
        print(mkt.cash_account, mkt.portfolio_account, mkt.market_account)
        print (value[value > 0].sum(), value[value < 0].sum())
        mkt.adjustPosition(tmp)
        #print ('postion: ', tmp)
        #print ('close: ', TodayPrice[:10])
    ret = mkt.next()
    dr.next()
    if ret == 0:
            break

#print('log:\n', mkt.stats.trading_log())
print('market stats:\n', mkt.stats.compute('monthly', isPlot=True))

#tmp = mkt.stats._market_info['ret']
#print('tmp:', tmp.mean(), tmp.std())

