from StocktrakAPI.API import Stocktrak_Broker
import pandas as pd
import joblib

position = pd.read_csv('OpenPosition_12_09_2018.csv', header=None)
broker = Stocktrak_Broker('credential.pkl', '../StocktrakAPI/chromedriver.exe')
basket = broker.createOrderBasket()
basket.orders, basket.order_placed = joblib.load('../StocktrakAPI/tmp_log.pkl')
print(basket.orders)
print(basket.order_placed)


for i in position.index:
    basket.add_order(*position.loc[i,:].tolist())

print(basket.orders)
broker.placeOrderBasket(basket)

basket.order_placed = joblib.load('../StocktrakAPI/tmp_log.pkl')
new_orders = {'Buy':[],
                       'Sell': [],
                       'Short': [],
                       'Cover': []}
for act in ['Buy', 'Sell', 'Cover', 'Short']:
    for order in basket.orders[act]:
        if order not in basket.order_placed[act]:
            new_orders[act].append(order)

new_orders['Sell'].remove(['AMD', 500])
new_orders['Short'].remove(['NBR', 4315])
new_orders['Sell'] = []
new_orders['Cover'] = []
basket.orders = new_orders.copy()
broker = Stocktrak_Broker('credential.pkl', '../StocktrakAPI/chromedriver.exe')
broker.placeOrderBasket(basket)





