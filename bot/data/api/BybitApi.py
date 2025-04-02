from decimal import Decimal

from pybit import exceptions

from bot.config.SecuredConfig import SecuredConfig
from bot.data.api.ApiHelpers import PositionType, float_trunc, round_down, floor_qty, floor_price
from bot.data.api.CoinPairInfo import CoinPairInfo
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent, StopLossIntent
from pybit.unified_trading import HTTP
import logging
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.TradingLogger import TradingLogger, RawTradingLog

MARKET_CATEGORY = "linear"

class BybitApi(BrokerApi):

    __client: HTTP
    __coin_pair_info: CoinPairInfo
    __trading_logger: TradingLogger
    __retry_request_fabric: RetryRequestHandlerFabric

    def __init__(
            self,
            trading_config: TradingConfig,
            trading_logger: TradingLogger,
            secured_config: SecuredConfig,
            retry_request_fabric:RetryRequestHandlerFabric,
    ):
        print("BybitApi init")
        self.__connect_to_api(trading_config, secured_config)
        self.__coin_pair_info = self.get_filters(trading_config)
        self.__set_leverage(trading_config)
        self.__trading_logger = trading_logger
        self.__retry_request_fabric = retry_request_fabric

    def __connect_to_api(self, trading_config: TradingConfig, secured_config: SecuredConfig):
        print("try to connect to Api")
        self.__client = HTTP(
            api_key=secured_config.get_broker_api_key(),
            api_secret=secured_config.get_broker_secret_key(),
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
        wallet_balance = wallet['totalAvailableBalance']
        print(f"totalAvailableBalance = {wallet_balance}")
        if wallet_balance is not None and wallet_balance != "":
            return float(wallet_balance)
        else:
            return 0.0

    def place_buy_order(self, long_intent: LongIntent):
        side = "Buy"
        pair_name = long_intent.trading_config.target_coin_name + long_intent.trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda : self.__place_order(
            coin_name=pair_name,
            asset_name = long_intent.trading_config.asset_name,
            side=side,
            trading_config=long_intent.trading_config,
        ))

    def place_sell_order(self, short_intent: ShortIntent):
        side = "Sell"
        pair_name = short_intent.trading_config.target_coin_name + short_intent.trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__place_order(
            coin_name=pair_name,
            asset_name = short_intent.trading_config.asset_name,
            side=side,
            trading_config=short_intent.trading_config,
        ))

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

        qty = qty * trading_config.leverage # умножаем количество на размер плеча

        order_message = f'''Тип сделки: Market\nВалюта: {coin_name}\nНаправление: {side}\nПлечо: {trading_config.leverage}\nКоличество: {qty} {trading_config.target_coin_name}\nРыночная цена: {curr_price} USDT\nНа кошельке: {available_assets} {asset_name}'''
        logging.debug("Параметры будующей сделки: \n" + str(order_message))

        result = self.__api_place_order(
            coin_name,
            side,
            qty,
            order_message,
        )
        log = RawTradingLog(
            coin_name=coin_name,
            side=side,
            leverage=str(trading_config.leverage),
            coin_price=str(curr_price),
            qty=qty,
            asset_name=asset_name,
            available_assets=str(available_assets),
        )
        self.__trading_logger.trade_log(log)
        return result

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
        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=coin_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            #qty=0.0000000000000000001
            qty=str(order_value),
        )

        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n"+ str(r))
        return "Совершена сделка:\n" + order_message

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
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        retry_handler.handle(lambda: self.__close_position(pair_name, side))


    def close_long_position(self, trading_config: TradingConfig):
        side = "Sell"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        retry_handler.handle(lambda: self.__close_position(pair_name, side))

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
        try:
            r = self.__client.set_leverage(
                category=MARKET_CATEGORY,
                symbol=trading_config.target_coin_name + trading_config.asset_name,
                buyLeverage=str(trading_config.leverage),
                sellLeverage=str(trading_config.leverage),
            )
            logging.debug(f"Set leverage: {str(r)}")
        except exceptions.InvalidRequestError as e:
            if e.status_code == 110043:
                logging.debug(f"Leverage {trading_config.leverage} was already set ")
            else:
                logging.error(f"InvalidRequestError set_leverage Error {e.message}")

    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__client_set_stop_loss(stop_loss_intent))

    def __client_set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        config: TradingConfig = stop_loss_intent.trading_config
        pair_name = config.target_coin_name + config.asset_name
        trigger_price = stop_loss_intent.trigger_price
        curr_price = self.get_price(pair_name)
        trigger_direction = 1 if trigger_price > curr_price else 2

        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=pair_name,
            side=stop_loss_intent.side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            qty=0.0,
            reduceOnly=True,
            closeOnTrigger=True,
            triggerPrice=floor_price(trigger_price, self.__coin_pair_info),
            triggerDirection=trigger_direction,
        )
        logging.debug(f"Set Stop Loss: {str(r)}")
        message = f'''Установлен STOP LOSS:\nТип сделки: Market\nВалюта: {pair_name}\nНаправление: {stop_loss_intent.side}\nУровень активации: {trigger_price} USDT\n'''
        return message

