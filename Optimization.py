import pandas as pd
import numpy as np
from scipy.optimize import minimize



def optimize(Dataset, weight, Beta, targetbeta):

	#targetbeta = 0.1

	def dollarneutral(weight):
	    weights = weight - sum(weight)/100
	    return  weights / sum(np.abs(weights))
	#print (dollarneutral(weight).head())
	scal = dollarneutral(weight)

	Dataprice = Dataset['Adj Close'][weight.index.values]
	data = Dataprice.iloc[-1000:,:]
	Return = np.log(data / data.shift(1))
	sig = Return.cov()

	delta = 0.0015
	a = scal - delta
	b = scal + delta
	bound = []
	for i in range(len(weight)):
	    temp = [a[i], b[i]]
	    bound.append(temp)

	def func1(w):
	    ww=np.array([w])
	    return np.dot(np.dot(ww,sig),ww.T)
	cons = ({'type':'eq','fun':lambda w: ((w*Beta).sum() - targetbeta)}
	        ,{'type':'ineq','fun':lambda w: np.abs(50 - (w > 0).sum())}
	        #,{'type':'ineq','fun':lambda w: (0.1 - np.abs((w[w>0].sum() + w[w<0].sum())/ w[w>0].sum()))}
	       )
	# cons=({'type':'ineq','fun':lambda w: sum(w) - 0.95},
	#      {'type': 'eq', 'fun': lambda w: sum(w * Exp) - r},
	#       {'type': 'ineq', 'fun': lambda w: sum(w * Beta) }
	#      )
	num = len(weight)
	res1=minimize(func1,num*[1/num], method='SLSQP',constraints = cons, bounds = bound)
	weights = pd.Series(res1.x, index = weight.index)
	weights = weights / sum(np.abs(weights))
	longpart = weights[weight > 0].sum()
	shortpart = weights[weight < 0].sum()

	print ('Newweights:', weights.head())
	print ('beta before: ',(weight * Beta).sum())
	print('beta after: ',(weights * Beta).sum())
	print ('Targe Beta:', targetbeta)
	print('positive stock', np.sum((weights > 0)).sum())
	print('Dollar nuetral:', np.sum(weights))
	print('Postive part:', longpart)
	print('Negative part:', shortpart)
	print('Variance:', (longpart + shortpart)/ longpart)

	return weights, (longpart + shortpart)/ longpart