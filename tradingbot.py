from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api.rest import REST
from timedelta import Timedelta

import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_URL = os.getenv('BASE_URL')

ALPACA_CREDS = {
    "API_KEY":API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

# life cyle methods
class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY", cash_at_risk:float=0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        # pass

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity =  round(cash * self.cash_at_risk / last_price,0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        print(f"Today: {today}, three_days_prior: {three_days_prior}")
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_news(self):
        try:
            today, three_days_prior = self.get_dates()
            news = self.api.get_news(symbol=self.symbol, 
                                 start=three_days_prior,
                                 end=today)

            news = [ev.__dict__["_raw"]["headline"] for ev in news]
            return news
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
        
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        # news = self.get_news
        # print(news)
        if cash > last_price:
            if self.last_trade == None:
                news = self.get_news()
                print(news)
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*0.95
                )
                self.submit_order(order)
                self.last_trade = "buy"
        # pass

start_date = datetime(2023, 12, 15)
end_date = datetime(2023, 12, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(
    name='mlstrat', 
    broker=broker, 
    parameters={"symbol": "SPY","cash_at_risk":0.5})

strategy.backtest(
    YahooDataBacktesting, 
    start_date, 
    end_date, 
    parameters={"symbol": "SPY","cash_at_risk":0.5}
)
