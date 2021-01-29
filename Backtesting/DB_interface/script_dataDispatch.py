import pandas as pd

data = pd.read_csv('./data/Dataset.csv', header=[0,1], index_col = 0)
features = ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']


for feature in features:
    tmp = data[feature]
    tmp.to_csv('data/'+feature+'.csv')

