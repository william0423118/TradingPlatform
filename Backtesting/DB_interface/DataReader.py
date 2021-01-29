import pandas as pd
import os
import sys
sys.path.append(os.getcwd()[:-12])
import DB_interface.Data as dt
#import ospytho

class dataReader:
    def __init__(self):
        self._close = dt.Close
        self.date_ls = list(self._close.index)
        self.today = self.date_ls[0]
        self.date_index = 0
        self.universe = list(self._close.columns)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.re_dir = os.path.join(dir_path,'./data')
        self.data = {}

        self.field = ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']

        self.init_data()

    def init_data(self):
        self.data = {}
        for f in self.field:
            self.data[f] = pd.read_csv(os.path.join(self.re_dir, f+'.csv'), index_col=0)

    def get(self, key, interval = 21):
        tmp = self.data[key].iloc[(self.date_index-interval+1):(self.date_index+1),:]
        return tmp.copy()

    def set_date(self, date):
        self.today = date
        self.date_index = self.date_ls.index(self.today)

    def next(self):
        self.date_index += 1
        self.today = self.date_ls[self.date_index]

if __name__=='__main__':
    a = dataReader()
    a.set_date('2017-10-26')
    #print(a.get('Open'))
    #a.next()
    print(a.get('Adj Close'))
    print(os.getcwd()[:-12])