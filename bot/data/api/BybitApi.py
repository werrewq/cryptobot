from decimal import Decimal

from bot.data.api.ApiHelpers import PositionType, float_trunc, round_down, floor_qty
from bot.data.api.CoinPairInfo import CoinPairInfo
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent
from pybit.unified_trading import HTTP
import logging

from bot.domain.dto.TradingConfig import TradingConfig

# Тестовые ключи
API_KEY = "6pAf7l2HZn46GqJqu6"
SECRET_KEY = "FHfaEudS6euKkiVobB6cDTkDzXs6TIBhX9Iu"
MARKET_CATEGORY = "linear"

# API_KEY = os.getenv("BB_API_KEY")
# SECRET_KEY = os.getenv("BB_SECRET_KEY")
class BybitApi(BrokerApi):

    __client: HTTP
    __coin_pair_info: CoinPairInfo

    def __init__(self, trading_config: TradingConfig):
        print("BybitApi init")
        self.__connect_to_api(trading_config)
        self.__coin_pair_info = self.get_filters(trading_config)
        self.__set_leverage(trading_config)


    def __connect_to_api(self, trading_config: TradingConfig):
        print("try to connect to Api")
        self.__client = HTTP(
            api_key=API_KEY,
            api_secret=SECRET_KEY,
            recv_window=60000,
            testnet=trading_config.testnet,
        )

    def get_filters(self, trading_config: TradingConfig) -> CoinPairInfo:
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        r = self.__client.get_instruments_info(
            category=MARKET_CATEGORY,
            symbol=pair_name,
        )
        c = r.get('result', {}).get('list', [])[0]
        min_qty = c.get('lotSizeFilter', {}).get('minOrderQty', '0.0')
        qty_raw = int(Decimal(min_qty).as_tuple().exponent)
        qty_decimals = abs(qty_raw)
        price_decimals = int(c.get('priceScale', '4'))
        min_qty = float(min_qty)

        return CoinPairInfo(
            price_decimals = price_decimals,
            qty_decimals = qty_decimals,
            min_qty = min_qty
        )

    def get_price(self, pair):
        """
        Один из способов получения текущей цены
        """
        tickers = self.__client.get_tickers(category=MARKET_CATEGORY, symbol=pair)
        r = float(tickers.get('result').get('list')[0].get('ask1Price'))
        return r

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

    def place_buy_order(self, long_intent: LongIntent):
        side = "Buy"
        pair_name = long_intent.trading_config.target_coin_name + long_intent.trading_config.asset_name
        return self.__place_order(
            coin_name=pair_name,
            asset_name = long_intent.trading_config.asset_name,
            side=side,
            trading_config=long_intent.trading_config,
        )

    def place_sell_order(self, short_intent: ShortIntent):
        side = "Sell"
        pair_name = short_intent.trading_config.target_coin_name + short_intent.trading_config.asset_name
        return self.__place_order(
            coin_name=pair_name,
            asset_name = short_intent.trading_config.asset_name,
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
        """
        Отправка ордера с размером позиции в Котируемой Валюте (USDT напр)
        имеет смысл только для контрактов
        (для спота есть аргумент marketUnit, см. https://youtu.be/e7Np2ICYBzg )
        """
        available_assets = self.get_assets(asset_name) # TODO поднять на уровень бизнесса, нужно понять на сколько это общая тема для разных API бирж
        curr_price = self.get_price(trading_config.target_coin_name + trading_config.asset_name)
        if asset_name == trading_config.target_coin_name: # продаем целевую валюту, для linear ордер считаем в ней
            assets_for_order = available_assets
            qty = assets_for_order
        else:  # если обмениваем USDT на что-то, то мы указываем количество целевой валюты к покупке, т.е. Nпокупка = Nusdt / CoinPrice
            assets_for_order = available_assets / 100 * trading_config.order_volume_percent_of_capital # cчитаем на сколько будем торговать
            qty = floor_qty(assets_for_order / curr_price, self.__coin_pair_info)  # переводим USDT в целевую валюту
        if qty < self.__coin_pair_info.min_qty: raise Exception(f"{qty} is to small")

        order_message = f'''Совершена сделка:\nТип сделки: Market\nВалюта: {coin_name}\nНаправление: {side}\nПлечо: {trading_config.leverage}\nКоличество: {qty} {trading_config.target_coin_name}\nРыночная цена: {curr_price} USDT\nНа кошельке: {available_assets} {asset_name}'''

        return self.__api_place_order(
            coin_name,
            side,
            qty,
            order_message,
        )

    # def place_market_order_by_base(self, qty : float = 0.00001, side : str = "Sell"):
    #     """
    #     Размещение рыночного ордера с указанием размера ордера в Базовой Валюте (BTC, XRP, etc)
    #     :param qty:
    #     :param side:
    #     :return:
    #     """
    #     args = dict(
    #         category=self.category,
    #         symbol=self.symbol,
    #         side=side.capitalize(),
    #         orderType="Market",
    #         qty=floor_qty(qty),
    #     )
    #     self.log("args", args)
    #
    #     r = self.cl.place_order(**args)
    #     self.log("result", r)
    #   return r

    def __api_place_order(
            self,
            coin_name,
            side,
            order_value,
            order_message,
    ):
        # TODO ошибка для linear pybit.exceptions.InvalidRequestError: Qty invalid (ErrCode: 10001) (ErrTime: 13:01:25). не верное количество
        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=coin_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            #qty=0.0000000000000000001
            qty=order_value,
        )

        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n"+ str(r))
        return order_message

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

    def have_order_long(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config, PositionType.LONG)

    def have_order_short(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config, PositionType.SHORT)

# TODO https://bybit-exchange.github.io/docs/v5/order/execution нужно проверить наличие лонгов/шортов, а не открытых ордеров
    def __have_order(self, trading_config: TradingConfig, position_type: PositionType):
        json = self.__client.get_positions(
            category = MARKET_CATEGORY,
            symbol = trading_config.target_coin_name + trading_config.asset_name
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
        self.__close_position(pair_name, side)

    def close_long_position(self, trading_config: TradingConfig):
        side = "Sell"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        self.__close_position(pair_name, side)

    def __close_position(self, pair_name, side):

        market_category = MARKET_CATEGORY # Не работает для SPOT
        r = self.__client.place_order(
            # category="linear",
            category=market_category,
            symbol=pair_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            # qty=0.0000000000000000001
            qty=0.0,
            reduceOnly=True,
            closeOnTrigger=True,
        )
        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n" + str(r))
        return str(r)

    def cancel_all_active_orders(self, trading_config: TradingConfig):
        symbol = trading_config.target_coin_name + trading_config.asset_name
        self.__client.cancel_all_orders(
            category = MARKET_CATEGORY,
            symbol = symbol
        )

    def __set_leverage(self, trading_config: TradingConfig):
        if trading_config.leverage <= 1:
            return
        r = self.__client.set_leverage(
            category=MARKET_CATEGORY,
            symbol=trading_config.target_coin_name + trading_config.asset_name,
            buyLeverage=str(trading_config.leverage),
            sellLeverage=str(trading_config.leverage),
        )
        logging.debug(f"Set leverage: {str(r)}")

