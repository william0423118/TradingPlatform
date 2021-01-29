from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import os
from selenium.webdriver.firefox.options import Options
import joblib
import pandas as pd
from selenium.webdriver.common.keys import Keys
import numpy as np
import time
from selenium.common.exceptions import TimeoutException

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

class PlaceOrderFailException(Exception):
    pass


class OrderBasket:
    def __init__(self, broker):
        self.broker = broker
        self.orders = {'Buy':[],
                       'Sell': [],
                       'Short': [],
                       'Cover': []}
        self._symbols = []
        self._orderType = self.orders.keys()
        self.order_placed = {'Buy':[],
                       'Sell': [],
                       'Short': [],
                       'Cover': []}

    def add_order(self, symbol, qty):
        assert symbol not in self._symbols, f'{symbol} has already been in this basket.'
        if type(qty) != int:
            qty = int(qty)
        seq = self.broker._action_type(symbol, qty)
        for act, qty_ in seq:
            # assert act in self._orderType, f'"{act}" is not one of the order types.'
            self.orders[act].append([symbol, qty_])
        self._symbols.append(symbol)

    def remove_order(self, symbol):
        assert symbol in self._symbols, f'{symbol} is not in this basket.'
        for act in self._orderType:
            tmp = np.array(self.orders[act])
            if len(tmp) == 0:
                continue
            keep_ls = []
            for i in range(tmp.shape[0]):
                if tmp[i,0] != symbol:
                    keep_ls.append(i)
            self.orders[act] = tmp[keep_ls,:].tolist()
        self._symbols.remove(symbol)

    def saveBasket(self, file):
        joblib.dump((self.orders, self.order_placed, self._symbols), file)

    def loadBasket(self, file):
        (self.orders, self.order_placed, self._symbols) = joblib.load(file)







class Stocktrak_Broker:
    def __init__(self, credential, executable_path):
        __credential = joblib.load(credential)

        # options = Options()
        # options.set_preference("browser.download.folderList", 2)
        # options.set_preference("browser.download.manager.showWhenStarting", False)
        # options.set_preference("browser.download.dir", f"{os.path.join(os.getcwd(),'data')}")
        # options.set_preference("browser.helperApps.neverAsk.saveToDisk",
        #                        "application/octet-stream,application/vnd.ms-excel, 'text/csv'")
        #
        #
        # self.driver = webdriver.Firefox(firefox_options=options, executable_path=executable_path)


        options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': f"{os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')}"}
        options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(chrome_options=options, executable_path=executable_path)


        self.driver.get('https://www.stocktrak.com/trading/equities')
        # self.driver.implicitly_wait(5)
        username = self.driver.find_element_by_id('tbLoginUserName')
        password = self.driver.find_element_by_id('Password')
        button = self.driver.find_element_by_xpath("//input[@value='Login']")

        username.clear()
        username.send_keys(__credential['account'])
        password.clear()
        password.send_keys(__credential['password'])
        button.click()

        self.action = {'Buy': 1,
                       'Sell': 2,
                       'Short': 3,
                       'Cover': 4}
        self.position = None
        self.portfolio = None
        self.update_portfolio()



    def placeMarketOrder(self, symbol_, quantity_):
        seq = self._action_type(symbol_, quantity_)
        for act, qnt in seq:
            self._placeOneOrder(act, symbol_, qnt)

    def createOrderBasket(self):
        return OrderBasket(self)

    def placeOrderBasket(self, basket, restore = None):

        act_ls = ['Sell', 'Cover', 'Buy', 'Short']
        # if restore:
        #     basket.orders, basket.order_placed = joblib.load(restore)
        #     basket_ = basket.orders
        # else:
        basket_ = basket.orders
        # basket.order_placed = joblib.load('tmp_log.pkl')
        for act in act_ls:
            for order in basket_[act]:
                if order in basket.order_placed[act]:
                    continue
                else:
                    print(f'placing {act}, {order}')
                    self._placeOneOrder(act, *order)
                    basket.order_placed[act].append(order)
                basket.saveBasket('tmp_log.pkl')



    def update_portfolio(self):
        self.portfolio = self._load_portfolio()
        tmp = self.portfolio.loc[:, ('Symbol', 'Quantity')]
        self.position = dict([tuple(tmp.iloc[row, :]) for row in range(tmp.index.size)])

    def close_position(self, symbol):
        self.update_portfolio()
        q = -self.position[symbol]
        self.placeMarketOrder(symbol, q)

    def _placeOneOrder(self, action, symbol_, quantity_):
        quantity_ = int(quantity_)
        if quantity_ == 0:
            return None
        # else:
        #     if quantity_ != int(quantity_):
        #         raise TypeError(f'quantity: {quantity_} not an int.')
        #     quantity_ = int(quantity_)
        self.driver.get('https://www.stocktrak.com/trading/equities')
        self.driver.implicitly_wait(3)

        orderside = self.driver.find_element_by_name('OrderSide')
        symbol = self.driver.find_element_by_name('Symbol')
        quantity = self.driver.find_element_by_name('Quantity')


        orderside.find_element_by_xpath(
            f"//option[@value='{self.action[action]}']").click()
        symbol.clear()
        symbol.send_keys(symbol_)
        # symbol.send_keys(Keys.ARROW_DOWN)
        # time.sleep(5)
        symbol.send_keys(Keys.TAB)
        quantity.clear()
        quantity.send_keys(str(abs(quantity_)))
        time.sleep(0.5)
        Preview_button = self.driver.find_element_by_id('btnPreviewOrder')
        Preview_button.click()

        self.driver.implicitly_wait(3)
        alerts = self.driver.find_elements_by_class_name('alert-box')
        for ele in alerts:
            print('Sys Alert: %s'%ele.text)


        for i in range(5):
            try:
                errors = self.driver.find_elements_by_class_name('errorMessage')
                for ele in errors:
                    if ele.text != '':
                        print('Sys Error: %s' % ele.text)
                        print(f'Order info: {action} {symbol_} {quantity_}')
                        raise PlaceOrderFailException(ele.text)
                    else:
                        pass
                confirm = WebDriverWait(self.driver, 2).until( \
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'a[id="btnPlaceOrder"]')))
                break
            except TimeoutException:
                print(f'TimeoutException: Retry: {i}')
                Preview_button = self.driver.find_element_by_id('btnPreviewOrder')
                Preview_button.click()


        confirm.click()
        post_info = WebDriverWait(self.driver, 5).until( \
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'div p[class="order-placed-txt"]'))).text
        # Only for market order
        if 'success' in post_info.lower():
            print('Order placed')
            print('System info: %s'%post_info)
            if symbol_ in self.position:
                new_value = self.position[symbol_] + quantity_
                if new_value != 0:
                    self.position[symbol_] = new_value
                else:
                    del self.position[symbol_]
            else:
                self.position[symbol_] = quantity_
        else:
            raise PlaceOrderFailException('Unknown condition.')


    def _load_portfolio(self):
        origin_page = self.driver.window_handles[0]
        self.driver.execute_script("window.open('about:blank', 'tab2');")
        position_page = self.driver.window_handles[-1]
        self.driver.switch_to.window(position_page)
        self.driver.get('https://www.stocktrak.com/account/openpositions')
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_id('btnExportToExcel').click()
        self.driver.implicitly_wait(10)
        tmp_btn = self.driver.find_element_by_id('btnExport')
        time.sleep(1)
        tmp_btn.click()
        file_path = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')}"
        while len(os.listdir(file_path))==0:
            time.sleep(0.1)
        time.sleep(5)
        ls = os.listdir(file_path)
        # try:
        #     ls.remove('.placeholder')
        # except:
        #     pass
        # if len(ls) != 1:
        #     raise FileNotFoundError('csv file not found or multiple csv file')
        portfolio = pd.read_csv(file_path+'/'+ls[0])
        os.remove(file_path+'/'+ls[0])
        self.driver.close()
        self.driver.switch_to.window(origin_page)
        return portfolio

    def _action_type(self, symbol, quantity):
        if type(quantity) != int:
            quantity = int(quantity)
        if symbol in self.position:
            current_pos = self.position[symbol]
            if quantity > 0:
                if current_pos < 0:
                    if current_pos + quantity <= 0:
                        return [('Cover', quantity)]
                    else:
                        return [('Cover', -current_pos), ('Buy', current_pos+quantity)]
                else:
                    return [('Buy', quantity)]
            else:
                if current_pos > 0:
                    if current_pos + quantity >= 0:
                        return [('Sell', -quantity)]
                    else:
                        return [('Sell', current_pos), ('Short', -(quantity+current_pos))]
                else:
                    return [('Short', -quantity)]
        else:
            if quantity > 0:
                return [('Buy', quantity)]
            else:
                return [('Short', -quantity)]

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

# #
if __name__=='__main__':
    position = pd.read_csv('./02_01_2019Diff.csv')
    broker = Stocktrak_Broker('credential.pkl', 'chromedriver.exe')
    basket = broker.createOrderBasket()

    # for i in position.index:
    #     basket.add_order(*position.iloc[i,[0,3]].tolist())
    #
    # print(basket.orders)

    basket.loadBasket('tmp_log.pkl')
    #

    broker.placeOrderBasket(basket)



