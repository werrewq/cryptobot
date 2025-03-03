import traceback
from zoneinfo import available_timezones

from unicodedata import category

from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.TradeIntent import ShortIntent, LongIntent
from pybit import exceptions
from pybit.unified_trading import HTTP
import logging
from enum import Enum

# Тестовые ключи
API_KEY = "6pAf7l2HZn46GqJqu6"
SECRET_KEY = "FHfaEudS6euKkiVobB6cDTkDzXs6TIBhX9Iu"

# API_KEY = os.getenv("BB_API_KEY")
# SECRET_KEY = os.getenv("BB_SECRET_KEY")
# TODO нужна вменяемая обработка ошибок
class BybitApi(BrokerApi):

    __client: HTTP

    def __init__(self):
        print("BybitApi init")
        self.__init_api_logging()
        self.__connect_to_api()

    def __init_api_logging(self):
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

    def __connect_to_api(self):
        print("try to connect to Api")
        self.__client = HTTP(
            api_key=API_KEY,
            api_secret=SECRET_KEY,
            recv_window=60000,
            testnet=True,
        )

    def get_assets(self, coin_name) -> float:
        """
        Получаю остатки на аккаунте по конкретной монете
        """

        r = self.__client.get_wallet_balance(accountType="UNIFIED", coin= coin_name)
        print(str(r))
        wallet_balance = None
        result = r['result']
        wallet = result['list'][0] #TODO может быть проблема, когда несколько кошельков
        coins = wallet['coin']
        for coin in coins:
            if coin['coin'] == coin_name:
                wallet_balance = coin['walletBalance']
                break
        print(f"wallet_balance = {wallet_balance}")
        if wallet_balance is not None:
            return float(wallet_balance)
        else:
            return 0.0

    def __get_coin_precision(self, pair_name, need_quote_precision) -> int:
        """
        :param need_quote_precision: хотим в паре BTCUSDT получить точность после запятой для USDT
        """
        r = self.__client.get_instruments_info(
            category = 'spot',
            symbol = pair_name,
        )
        result = r['result']
        pair = result['list'][0]
        lot_size_filter = pair['lotSizeFilter']
        precision_example = lot_size_filter['basePrecision']
        if need_quote_precision:
            precision_example = lot_size_filter['quotePrecision']
        return self.__count_decimal_places(precision_example)


    def __count_decimal_places(self, str_number: str) -> int:
        # Проверяем, есть ли дробная часть
        if '.' in str_number:
        # Возвращаем количество знаков после запятой
            return len(str_number.split('.')[1])
        return 0  # Если дробной части нет

        # второй вариант для точности после запятой
        # r = self.__client.get_coin_info(coin=coin_name)
        # result = r['result']
        # rows_list = result['rows']
        # chains_list = []
        # for row in rows_list:
        #     if row['coin'] == coin_name:
        #         chains_list = row['chains']
        #         break

    def place_buy_order(self, long_intent: LongIntent):
        side = "Buy"
        return self.__place_order(coin_name=long_intent.currency_name + "USDT", asset_name = "USDT",side=side)

    # api.place_order(name_coin_u, "Sell", 10)
    def place_sell_order(self, short_intent: ShortIntent):
        side = "Sell"
        return self.__place_order(coin_name=short_intent.currency_name +"USDT", asset_name = short_intent.currency_name,side=side)

    def __place_order(self, coin_name, asset_name, side) -> str:
        # TODO доделать лимитки assets
        available_assets = self.get_assets(asset_name)
        # TODO доделать установку объема
        available_assets = available_assets / 100
        need_quote_precision = False
        if side == "Buy":
            need_quote_precision = True
        min_precision = self.__get_coin_precision(coin_name, need_quote_precision)
        order_value = float_trunc(available_assets, min_precision)
        market_category = "spot"
        return self.__api_place_order(
            coin_name,
            side,
            market_category,
            order_value,
        )

    def __api_place_order(self, coin_name, side, market_category, order_value):
        # r = cl.get_instruments_info(category="spot", symbol="SOLUSDT")
        # print(r)
        r = self.__client.place_order(
            # category="linear",
            category=market_category,
            symbol=coin_name, # USDT и Name меняются местами
            side=side,
            orderType="Market",
            # qty=0.0000000000000000001
            qty=order_value,
            # marketUnit="quoteCoin",
        )
        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n"+ str(r))
# TODO убрать
        order_history = self.__client.get_order_history(category=market_category)
        logging.debug("CПИСОК ОРДЕРОВ \n" + str(order_history))
        return str(r)

    def __place_limit_order(self, name, side, price):
        # r = cl.get_instruments_info(category="spot", symbol="SOLUSDT")
        # print(r)
        self.__client.get_instruments_info(category="spot", symbol="SOLUSDT")
        available = self.get_assets(name)
        print(available, round(available, 3), float_trunc(available, 3), float_trunc(available, 3))

        r = self.__client.place_order(
            category="linear",
            symbol=name + "USDT", # USDT и Name меняются местами
            side=side,
            orderType="Market",
            qty=float_trunc(available, 3),
            # marketUnit="quoteCoin", TODO торгует через USDT при SELL BTC
        )
        r = self.__client.place_order(
            category="spot",
            symbol=name + "USDT", # USDT и Name меняются местами
            side=side,
            orderType="Limit",
            qty=float_trunc(available, 3),
            price=round_down(price * 0.99, 2),
        )

        print(str(r))
        return str(r)


        #
        #
        # v = "{:.3f}".format(round(self.__get_balance("USDT") / 5) / float(self.get_price(name + "USDT")))
        # return (self._session_auth_perp.place_active_order(
        #     symbol=name + "USDT",
        #     side=position,
        #     order_type="Market",
        #     qty=v,
        #     time_in_force="GoodTillCancel",
        #     reduce_only=False,
        #     close_on_trigger=False
        # ))

    class PositionType(Enum):
        LONG = "Buy"
        SHORT = "Sell"

    def have_order_long(self, currency_name) -> bool:
        return self.__have_order(currency_name, self.PositionType.LONG,category_type = "inverse")

    def have_order_short(self, currency_name) -> bool:
        return self.__have_order(currency_name, self.PositionType.SHORT, category_type = "linear")

    def __have_order(self, currency_name, position_type: PositionType, category_type):
        json = self.__client.get_positions(
            category = category_type,
            symbol = currency_name + "USDT"
        )
        print(str(json))
        have_order = False
        positions = json['result']
        for position in positions['list']:
            if position['side'] == position_type.value:
                have_order = True
        return have_order

    def __close_position(self, currency_name, side):
        pass
        # try:
        #     # Закрытие позиции
        #     # response = self.__client.(
        #     #     symbol=currency_name + "USDT",
        #     #     side=side
        #     # )
        #     # print("Ответ от API:", response)
        # except Exception as e:
        #     print("Ошибка:", e)

    # api.close_position(name_coin_u, "Buy", 1)
    def close_short_position(self, currency_name):
        side = "Buy"
        self.__close_position(currency_name, side, self.PositionType.SHORT.value)

    # api.close_position(name_coin_u, "Sell", 0)
    def close_long_position(self, currency_name):
        side = "Sell"
        self.__close_position(currency_name, side, self.PositionType.LONG.value)

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

    def cancel_all_active_orders(self):
        self.__client.cancel_all_orders(
            category = "spot"
        )

def float_trunc(f, prec):
    """
    Ещё один способ отбросить от float лишнее без округлений
    :param f:
    :param prec:
    :return:
    """
    l, r = f"{float(f):.12f}".split('.') # 12 дб достаточно для всех монет
    return  float(f'{l}.{r[:prec]}')

def round_down(value, decimals):
    """
    Ещё один способ отбросить от float лишнее без округлений
    :return:
    """
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

