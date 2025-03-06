from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.dto.TradeIntent import ShortIntent, LongIntent
from pybit.unified_trading import HTTP
import logging
from enum import Enum

from Bot.domain.dto.TradingConfig import TradingConfig

# Тестовые ключи
API_KEY = "6pAf7l2HZn46GqJqu6"
SECRET_KEY = "FHfaEudS6euKkiVobB6cDTkDzXs6TIBhX9Iu"
MARKET_CATEGORY = "linear"

# API_KEY = os.getenv("BB_API_KEY")
# SECRET_KEY = os.getenv("BB_SECRET_KEY")
class BybitApi(BrokerApi):

    __client: HTTP

    def __init__(self, trading_config: TradingConfig):
        print("BybitApi init")
        self.__connect_to_api(trading_config)

    def __connect_to_api(self, trading_config: TradingConfig):
        print("try to connect to Api")
        self.__client = HTTP(
            api_key=API_KEY,
            api_secret=SECRET_KEY,
            recv_window=60000,
            testnet=trading_config.testnet,
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
        if wallet_balance is not None and wallet_balance != "":
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
        pair_name = long_intent.trading_config.target_coin_name + long_intent.trading_config.asset_name
        return self.__place_order(
            coin_name=pair_name,
            asset_name = long_intent.trading_config.asset_name,
            side=side,
            trading_config=long_intent.trading_config,
        )

    # api.place_order(name_coin_u, "Sell", 10)
    def place_sell_order(self, short_intent: ShortIntent):
        side = "Sell"
        pair_name = short_intent.trading_config.target_coin_name + short_intent.trading_config.asset_name
        return self.__place_order(
            coin_name=pair_name,
            asset_name = short_intent.trading_config.target_coin_name,
            side=side,
            trading_config=short_intent.trading_config,
        )

    def __place_order(
            self,
            coin_name,
            asset_name,
            side,
            trading_config: TradingConfig
    ) -> str:
        # TODO доделать лимитки assets
        available_assets = self.get_assets(asset_name) # TODO поднять на уровень бизнесса, нужно понять на сколько это общая тема для разных API бирж
        available_assets = available_assets / 100 * trading_config.order_volume_percent_of_capital
        need_quote_precision = False
        if side == "Buy":
            need_quote_precision = True
        min_precision = self.__get_coin_precision(coin_name, need_quote_precision)
        order_value = float_trunc(available_assets, min_precision)
        market_category = MARKET_CATEGORY
        return self.__api_place_order(
            coin_name,
            side,
            market_category,
            order_value,
        )

    def __api_place_order(self, coin_name, side, market_category, order_value):
        # TODO ошибка для linear pybit.exceptions.InvalidRequestError: Qty invalid (ErrCode: 10001) (ErrTime: 13:01:25). не верное количество
        r = self.__client.place_order(
            category=market_category,
            symbol=coin_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            #qty=0.0000000000000000001
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
            category=MARKET_CATEGORY,
            symbol=name + "USDT", # USDT и Name меняются местами
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            qty=float_trunc(available, 3),
            # marketUnit="quoteCoin", TODO торгует через USDT при SELL BTC
        )
        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=name + "USDT", # USDT и Name меняются местами
            side=side,
            orderType="Limit",
            time_in_force="GoodTillCancel",
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

    def have_order_long(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config.target_coin_name, self.PositionType.LONG,category_type = MARKET_CATEGORY)

    def have_order_short(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config.target_coin_name, self.PositionType.SHORT, category_type = MARKET_CATEGORY)

# TODO https://bybit-exchange.github.io/docs/v5/order/execution нужно проверить наличие лонгов/шортов, а не открытых ордеров
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

    def close_short_position(self, trading_config: TradingConfig):
        side = "Buy"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        self.__close_position(pair_name, side, asset_name=trading_config.asset_name)

    def close_long_position(self, trading_config: TradingConfig):
        side = "Sell"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        self.__close_position(pair_name, side, trading_config.asset_name)

    def __close_position(self, pair_name, side,  asset_name):
        # TODO доделать лимитки assets
        available_assets = self.get_assets(asset_name) # TODO маркет может меняться
        # TODO доделать установку объема
        need_quote_precision = False
        if side == "Buy":
            need_quote_precision = True
        min_precision = self.__get_coin_precision(pair_name, need_quote_precision)
        order_value = float_trunc(available_assets, min_precision)

        market_category = MARKET_CATEGORY # Не работает для SPOT
        r = self.__client.place_order(
            # category="linear",
            category=market_category,
            symbol=pair_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            # qty=0.0000000000000000001
            qty=order_value,
            reduce_only=True
            # marketUnit="quoteCoin",
        )
        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n" + str(r))
        # TODO убрать
        order_history = self.__client.get_order_history(category=market_category)
        logging.debug("CПИСОК ОРДЕРОВ \n" + str(order_history))
        return str(r)



    def cancel_all_active_orders(self, trading_config: TradingConfig):
        symbol = trading_config.target_coin_name + trading_config.asset_name
        self.__client.cancel_all_orders(
            category = MARKET_CATEGORY,
            symbol = symbol
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

