import logging
from enum import Enum

# from pybit.unified_trading import HTTP

from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.TradeIntent import LongIntent, ShortIntent
from pybit import inverse_perpetual, HTTP
from pybit import usdt_perpetual


API_KEY = "API_KEY"
SECRET_KEY = "SECRET_KEY"

# endpoint = "https://api.bybit.com"
endpoint = "https://api-testnet.bybit.com"

#TODO Перейти на pybit==5.9.0
class BybitApi(BrokerApi):

    # _session: HTTP = None

    _session_unauth: HTTP
    _session_auth_inverse: HTTP
    _session_auth_perp: HTTP

    class PositionType(Enum):
        LONG = 0
        SHORT = 1

    def __init__(self):
        print("BybitApi init")
        self.__init_api_logging()
        self.__connect_to_api()

    def __connect_to_api(self):
        print("try to connect to Api")
        # self._session = HTTP(
        #     api_key = API_KEY,
        #     api_secret = SECRET_KEY,
        #     testnet = True, # Тестовые запросы для торговли
        #     recv_window = 60000 #TODO Лучше сделать точное совпадение времени на хосте см. NTPD
        # )
        self._session_unauth = inverse_perpetual.HTTP(
            endpoint=endpoint
        )

        self._session_auth_inverse = inverse_perpetual.HTTP(
            endpoint=endpoint,
            api_key=API_KEY,
            api_secret=SECRET_KEY
        )

        self._session_auth_perp = usdt_perpetual.HTTP(
            endpoint=endpoint,
            api_key=API_KEY,
            api_secret=SECRET_KEY
        )

    def __init_api_logging(self):
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

    def get_position(self, currency_name):
        return self._session_auth_perp.my_position(symbol=currency_name)

    def have_order_long(self, currency_name) -> bool:
        return self.__have_order(currency_name, BybitApi.PositionType.LONG)

    def have_order_short(self, currency_name) -> bool:
        return self.__have_order(currency_name, BybitApi.PositionType.SHORT)

    def __have_order(self, symbol, position_type: PositionType):
        json = self.get_position(symbol + "USDT")
        size = json["result"][position_type.value]['size']
        if size != 0:
            return True
        return False

    def place_buy_order(self, long_intent: LongIntent):
        leverage = 10 #TODO ЧТО ЭТО?!!!
        side = "Buy"
        return self.__place_order(long_intent.currency_name, side, leverage)

    # api.place_order(name_coin_u, "Sell", 10)
    def place_sell_order(self, short_intent: ShortIntent):
        leverage = 10  #TODO ЧТО ЭТО?!!!
        side = "Sell"
        return self.__place_order(short_intent.currency_name, side, leverage)

    # api.close_position(name_coin_u, "Buy", 1)
    def close_short_position(self, currency_name):
        side = "Buy"
        self.__close_position(currency_name, side, BybitApi.PositionType.SHORT.value)

    # api.close_position(name_coin_u, "Sell", 0)
    def close_long_position(self, currency_name):
        side = "Sell"
        self.__close_position(currency_name, side, BybitApi.PositionType.LONG.value)

    def __close_position(self, name, side, long_0_short_1):
        return (self._session_auth_perp.place_active_order(
            symbol=name + "USDT",
            side=side,
            order_type="Market",
            qty=self.__get_position_qty(name + "USDT", long_0_short_1),
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=False
        ))

    def __get_position_qty(self, name, long_0_short_1):
        return self.get_position(name)["result"][long_0_short_1]["size"]

    def __get_balance(self, name):
        return (self._session_auth_inverse.get_wallet_balance(coin=name))["result"][name]["available_balance"]

    def get_price(self, name):
        return (self._session_unauth.latest_information_for_symbol(
            symbol=name
        )['result'][0]['last_price'])

    def __place_order(self, name, position, leverage):
        v = "{:.3f}".format(round(self.__get_balance("USDT") / 5 * leverage) / float(self.get_price(name + "USDT")))
        return (self._session_auth_perp.place_active_order(
            symbol=name + "USDT",
            side=position,
            order_type="Market",
            qty=v,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        ))

    # def get_order_book(self):
    #     try:
    #         return self._session.get_orderbook(category="linear", symbol="BTCUSDT")
    #     except exceptions.FailedRequestError as e:
    #         print(e.message)
    #         return None

    # def place_market_order(self):
    #     # Добавить аргументы
    #     result = self._session.place_order(
    #         category = "spot",
    #         symbol = "ALGOUSDT",
    #         side = "BUY",
    #         orderType = "Market",
    #         qty = "1000000", # В ALGOUSDT количество USDT которое хотим потратить на покупку, при продаже количество ALGO, которое хотим купить ВАЖНО! не на споте, работает по другому
    #         # marketUnit = baseCoin, # Если хотим, чтобы указывалось чисто в USDT валюте
    #
    #     )
    #
    # def get_wallet_balance(self):
    #     result = self._session.get_wallet_balance(
    #         accountType = "UNIFIED"
    #     )
    #
    # def get_coin_sell_parameters_infor(self):
    #     result = self._session.get_instruments_info(
    #         category = "spot",
    #         symbol = "ALGOUSDT",
    #     )