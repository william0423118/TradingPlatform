## Dependency:
 - selenium
 - joblib
 
## Selenium WebDriver
- Selenium WebDriver is one of the most popular tools for **Web UI Automation**
- Installation:
  - Install Selenium package: 
    - pip install selenium
  - Download a webdirver based on your browser
    - Chrome:	https://sites.google.com/a/chromium.org/chromedriver/downloads
    - Firefox:	https://github.com/mozilla/geckodriver/releases
    - Safari:	https://webkit.org/blog/6900/webdriver-support-in-safari-10/
  - Here we use **Firefox**. **Driver for Windows has been included in this repo, Mac user need to download corresponding driver.**
## Introduction
- When you use this package, I assume you only use this package to place order, and only one broker is populated, or position calculator will fail otherwise.
- Credential file, `credential.pkl`, is Not in this repository.
- `data` folder is to save temporary data file. Do not touch.

## Interface
- **Method**
    - `__init__(self, credential, executable_path = './geckodriver.exe')`: `credential`: str, pickle file path; `executable_path`: path to Web driver.
    - `placeMarketOrder(self, symbol_, quantity_)`: `symbol_`: str, `quantity_`: int, (negative value indicates sell or short)
    - `update_portfolio(self)`:  update `self.portfolio` and `self.position`.
    - `close_position(self, symbol)`: `symbol`: str, the symbol whose open position need to be closed.
    - `createOrderBasket()`: return a `OrderBasket` object, use `basket.add_order(symbol, qty)` and `basket.remove_order(symbol)` to add or remove order from this basket. __One symbol can only be add once to one basket__ (this is to protect position correctness). See example below for detail.
- **Data**
    - `self.portfolio`: Pandas dataframe, shows all information of open position.
    - `self.position`: dict, where keys are symbols, and values are positons.
    
## Example
```python
from StocktrakAPI.API import Stocktrak_Broker

with Stocktrak_Broker('credential.pkl') as broker:
    # Suppose we do not hold AAPL at begining
    
    broker.placeMarketOrder('AAPL', 10) # place a buy order of 10 for AAPL, position is 10 if successful.
    broker.placeMarketOrder('AAPL', -30) # place a sell order of 10, a short order of 20 for AAPL, position is -20 if successful.
    broker.close_position('AAPL') # close AAPL's open position
    print(broker.portfolio)
    print(broker.position)
    basket = broker.createOrderBasket()
    basket.add_order('AAPL', 100)
    basket.add_order('GOOG', 20)
    basket.add_order('GE', -40)
    basket.add_order('AR', 500)
    print(basket.orders)
    basket.remove_order('GOOG')
    print(basket.orders)
    broker.placeOrderBasket(basket)
    
# output
#First print of basket.orders: 
# {'Buy': [['AAPL', 100], ['GOOG', 11], ['AR', 239]], 'Sell': [['GE', 40]], 'Short': [], 'Cover': [['GOOG', 9], ['AR', 261]]}
#basket.orders after removal of 'GOOG' order:
# {'Buy': [['AAPL', '100'], ['AR', '239']], 'Sell': [['GE', '40']], 'Short': [], 'Cover': [['AR', '261']]}
#placing Sell, ['GE', '40']
#placing Cover, ['AR', '261']
#placing Buy, ['AAPL', '100']
#placing Buy, ['AR', '239']

```
