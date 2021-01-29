import pandas as pd
import numpy as np
def scale(data):
    data = data.dropna()
    ret = data - np.mean(data)
    ret = 2*ret/np.sum(np.abs(ret))
    return ret

def getRSI(Dataset):

	todayprice = Dataset['Adj Close'].iloc[-1,:]
	TodayPrice = todayprice.dropna()
	TodayPrice = TodayPrice[TodayPrice > 5]

	Dataset.index = pd.to_datetime(Dataset.index)
	NewdataW = Dataset.resample('W').last()
	Close_Price = NewdataW['Adj Close'][TodayPrice.index]

	def RSI(df, num):
	    # wilder's RSI
	    period=14
	    delta = df.diff()
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
	    return (rsi_sorted[0:num], rsi_sorted[-num:])
	rsi1, rsi2 = RSI(Close_Price, num = 50)

	weight = pd.concat([rsi1-50,rsi2-50])

	return weight

def MA(Close,short, long):
    Short = Close.iloc[-short:,:].mean()
    Long = Close.iloc[-long:,:].mean()
    sig = (Short - Long).sort_values().dropna()
    return -scale(pd.concat([sig[0:50], sig[-50:]]))

def Momentum(Dataset, num): 
	todayprice = Dataset['Adj Close'].iloc[-1,:]
	TodayPrice = todayprice.dropna()
	TodayPrice = TodayPrice[TodayPrice > 5]
	Dataset.index = pd.to_datetime(Dataset.index)
	NewdataW = Dataset.resample('W').last()
	Close_Price = NewdataW['Adj Close'][TodayPrice.index]

	close = Close_Price
	Alpha =  close.iloc[-1,:]/close.iloc[-num,:] - 1
	OrderAlpha = Alpha.sort_values().dropna()
	return scale(pd.concat(([OrderAlpha[0:50], OrderAlpha[-50:]])))


def KDJ(Dataset, nDay):
	todayprice = Dataset['Adj Close'].iloc[-1,:]
	TodayPrice = todayprice.dropna()
	TodayPrice = TodayPrice[TodayPrice > 5]
	Dataset.index = pd.to_datetime(Dataset.index)
	NewdataW = Dataset.resample('W').last()
	Close= NewdataW['Adj Close'][TodayPrice.index]
	Low = NewdataW['Low'][TodayPrice.index]
	High = NewdataW['High'][TodayPrice.index]

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
	    #print (RSV)
	    K.iloc[i,:] = 2/3 * K.iloc[i-1,:] + 1/3 * RSV
	    D.iloc[i,:] = 2/2 *K.iloc[i-1,:] + 1/3 * K.iloc[i,:]
	#print (K.iloc[-5:,:], D.iloc[-5:,])
	kdj = (D.iloc[-1, :] - K.iloc[-1,:]).sort_values().dropna()

	return scale(pd.concat([kdj[0:50], kdj[-50:]]))


if __name__ == "__main__":

	Dataset = pd.read_csv('dataset/Dataset.csv', header = [0, 1], index_col = 0)
	#weight =getRSI(Dataset).add(MA(Dataset['Adj Close'], 5, 10), fill_value = 0)
	#weight = Momentum(Dataset, 5)
	weight = -KDJ(Dataset, nDay = 14 )
	print (weight)
