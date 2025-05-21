import logging
from decimal import Decimal

from pybit import exceptions

from bot.data.api.ApiHelpers import PositionType, floor_qty
from bot.data.api.BybitApi import BybitApi
from bot.data.api.CoinPairInfo import CoinPairInfo
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import StopLossIntent, ShortIntent, LongIntent, TakeProfitIntent
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.TradingLogger import RawTradingLog, TradingLogger


class BybitInteractor(BrokerApi):

    __bybit_api: BybitApi
    __retry_request_fabric: RetryRequestHandlerFabric
    __coin_pair_info: CoinPairInfo
    __trading_logger: TradingLogger

    def __init__(
            self,
            bybit_api: BybitApi,
            retry_request_fabric: RetryRequestHandlerFabric,
            trading_logger: TradingLogger,
            trading_config: TradingConfig,
            ):
        self.__bybit_api = bybit_api
        self.__retry_request_fabric = retry_request_fabric
        self.__trading_logger = trading_logger
        self.__coin_pair_info = self.get_filters(trading_config)
        self.__set_leverage(trading_config)

    def get_filters(self, trading_config: TradingConfig) -> CoinPairInfo:
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        r = self.__bybit_api.get_instruments_info(pair_name)
        c = r.get('result', {}).get('list', [])[0]
        min_qty = c.get('lotSizeFilter', {}).get('minOrderQty', '0.0')
        qty_raw = int(Decimal(min_qty).as_tuple().exponent)
        qty_decimals = abs(qty_raw)
        price_decimals = int(c.get('priceScale', '4'))
        min_qty = float(min_qty)

        logging.debug(f"Got filters for {pair_name}:\nprice_decimals={str(price_decimals)}\nqty_decimals={str(qty_decimals)}\nmin_qty={str(min_qty)}")

        return CoinPairInfo(
            price_decimals = price_decimals,
            qty_decimals = qty_decimals,
            min_qty = min_qty
        )

    def __set_leverage(self, trading_config: TradingConfig):
        try:
            r = self.__bybit_api.set_leverage(trading_config)
            logging.debug(f"Set leverage: {str(r)}")
        except exceptions.InvalidRequestError as e:
            if e.status_code == 110043:
                logging.debug(f"Leverage {trading_config.leverage} was already set ")
            else:
                logging.error(f"InvalidRequestError set_leverage Error {e.message}")

    def get_price(self, pair):
        tickers = self.__bybit_api.get_tickers(pair)
        r = float(tickers.get('result').get('list')[0].get('ask1Price'))
        logging.debug(f"current price {pair} = {str(r)}")
        return r

    def get_total_available_balance(self, asset_name) -> float:
        """
        Получаю остатки на аккаунте по активам: пример USDT
        """
        r = self.__bybit_api.get_wallet_balance(asset_name)
        print(str(r))
        wallet_balance = None
        result = r['result']
        wallet = result['list'][0] #TODO может быть проблема, когда несколько кошельков
        wallet_balance = wallet['totalAvailableBalance']
        logging.debug(f"totalAvailableBalance = {wallet_balance}")
        if wallet_balance is not None and wallet_balance != "":
            return float(wallet_balance)
        else:
            return 0.0

    def get_target_coin_balance(self, target_coin_name) -> float:
        """
        Получаю остатки на аккаунте по конкретной монете
        """
        r = self.__bybit_api.get_wallet_balance(target_coin_name)
        print(str(r))
        result = r['result']
        logging.debug(f"result = {str(result)}")
        wallet = result['list'][0] #TODO может быть проблема, когда несколько кошельков
        coins = wallet['coin']
        for coin in coins:
            if coin['coin'] == target_coin_name:
                logging.debug(f"walletBalance = {coin['walletBalance']}")
                return float(coin['walletBalance'])
        return 0.0

    def have_order_long(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config, PositionType.LONG)

    def have_order_short(self, trading_config: TradingConfig) -> bool:
        return self.__have_order(trading_config, PositionType.SHORT)

    def __have_order(self, trading_config: TradingConfig, position_type: PositionType):
        json = self.__bybit_api.get_positions(trading_config)
        print(str(json))
        have_order = False
        positions = json['result']
        for position in positions['list']:
            if position['side'] == position_type.value:
                have_order = True
        return have_order

    def close_short_position(self, trading_config: TradingConfig):
        logging.debug(f"close_short_position")
        side = "Buy"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        retry_handler.handle(lambda: self.__bybit_api.close_position(pair_name, side))

    def close_long_position(self, trading_config: TradingConfig):
        logging.debug(f"close_long_position")
        side = "Sell"
        pair_name = trading_config.target_coin_name + trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        retry_handler.handle(lambda: self.__bybit_api.close_position(pair_name, side))

    def place_buy_order(self, long_intent: LongIntent):
        side = "Buy"
        pair_name = long_intent.trading_config.target_coin_name + long_intent.trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda : self.__prepare_order(
            coin_name=pair_name,
            asset_name = long_intent.trading_config.asset_name,
            side=side,
            trading_config=long_intent.trading_config,
        ))

    def place_sell_order(self, short_intent: ShortIntent):
        side = "Sell"
        pair_name = short_intent.trading_config.target_coin_name + short_intent.trading_config.asset_name
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__prepare_order(
            coin_name=pair_name,
            asset_name = short_intent.trading_config.asset_name,
            side=side,
            trading_config=short_intent.trading_config,
        ))

    def __prepare_order(
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
        available_assets = self.get_total_available_balance(asset_name)
        curr_price = self.get_price(trading_config.target_coin_name + trading_config.asset_name)
        if asset_name == trading_config.target_coin_name: # продаем целевую валюту, для linear ордер считаем в ней
            assets_for_order = available_assets
            qty = assets_for_order
        else:  # если обмениваем USDT на что-то, то мы указываем количество целевой валюты к покупке, т.е. Nпокупка = Nusdt / CoinPrice
            assets_for_order = available_assets / 100 * trading_config.order_volume_percent_of_capital # cчитаем на сколько будем торговать
            qty = assets_for_order / curr_price  # переводим USDT в целевую валюту

        qty = qty * trading_config.leverage # умножаем количество на размер плеча
        qty = floor_qty(qty, self.__coin_pair_info)

        if qty < self.__coin_pair_info.min_qty: raise Exception(f"{qty} is to small")

        order_message = f'''Тип сделки: Market\nВалюта: {coin_name}\nНаправление: {side}\nПлечо: {trading_config.leverage}\nКоличество: {qty} {trading_config.target_coin_name}\nРыночная цена: {curr_price} USDT\nНа кошельке: {available_assets} {asset_name}'''

        result = self.__bybit_api.place_order(
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

    def cancel_all_active_orders(self, trading_config: TradingConfig):
        symbol = trading_config.target_coin_name + trading_config.asset_name
        self.__bybit_api.cancel_all_active_orders(symbol)

    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__client_set_stop_loss(stop_loss_intent))

    def __client_set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        config: TradingConfig = stop_loss_intent.trading_config
        pair_name = config.target_coin_name + config.asset_name
        trigger_price = stop_loss_intent.trigger_price

        if stop_loss_intent.side == "Sell":
            trigger_direction = 2 # Fall to price
        else:
            trigger_direction = 1 # Raise to price

        r = self.__bybit_api.set_stop_loss(pair_name, stop_loss_intent.side, trigger_direction, floor_qty(trigger_price, self.__coin_pair_info))
        logging.debug(f"Set Stop Loss: {str(r)}")
        message = f'''Установлен STOP LOSS:\nВалюта: {pair_name}\nНаправление: {stop_loss_intent.side}\nУровень активации: {trigger_price} USDT\n'''
        return message

    def set_take_profit(self, take_profit_intent: TakeProfitIntent) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__set_take_profit(take_profit_intent))

    def __set_take_profit(self, take_profit_intent: TakeProfitIntent) -> str:
        if take_profit_intent.market:
            return self.__set_market_take_profit(take_profit_intent)

        config: TradingConfig = take_profit_intent.trading_config
        pair_name = config.target_coin_name + config.asset_name
        trigger_price = take_profit_intent.trigger_price

        if take_profit_intent.side == "Sell":
            trigger_direction = 1 # Raise to price
        else:
            trigger_direction = 2  # Fall to price

        qty = self.__count_take_profit_qty(take_profit_intent)

        r = self.__bybit_api.set_take_profit(pair_name, take_profit_intent.side, trigger_direction, floor_qty(trigger_price,self.__coin_pair_info), qty)
        logging.debug(f"Set Take profit: {str(r)}")
        message = f'''Установлен TAKE PROFIT:\nТип сделки: Market\nВалюта: {pair_name}\nНаправление: {take_profit_intent.side}\nУровень активации: {trigger_price} USDT\n Количество ордеров в TP: {qty}'''
        return message

    def __set_market_take_profit(self, take_profit_intent: TakeProfitIntent) -> str:
        qty = self.__count_take_profit_qty(take_profit_intent)
        pair_name = take_profit_intent.trading_config.target_coin_name + take_profit_intent.trading_config.asset_name
        curr_price = self.get_price(pair_name)
        available_assets = self.get_total_available_balance(take_profit_intent.trading_config.asset_name)

        order_message = f'''Тип сделки: Market\nВалюта: {pair_name}\nНаправление: {take_profit_intent.side}\nПлечо: {take_profit_intent.trading_config.leverage}\nКоличество: {qty} {take_profit_intent.trading_config.target_coin_name}\nРыночная цена: {curr_price} USDT\nНа кошельке: {available_assets} {take_profit_intent.trading_config.asset_name}'''
        self.__bybit_api.place_order(
            coin_name = pair_name,
            side=take_profit_intent.side,
            order_value=qty,
            order_message=order_message,
        )
        log = RawTradingLog(
            coin_name=pair_name,
            side=take_profit_intent.side,
            leverage=str(take_profit_intent.trading_config.leverage),
            coin_price=str(curr_price),
            qty=str(qty),
            asset_name=take_profit_intent.trading_config.asset_name,
            available_assets=str(available_assets),
        )
        self.__trading_logger.trade_log(log)

        message = f'''Забираем TAKE PROFIT по Маркету :\n''' + order_message
        return message

    def __count_take_profit_qty(self, take_profit_intent) -> float:
        full_position_qty = self.get_target_coin_balance(take_profit_intent.trading_config.target_coin_name + take_profit_intent.trading_config.asset_name)
        logging.debug(f"full_position_qty = {str(full_position_qty)}")
        logging.debug(f"take_profit_percentage_from_order = {str(take_profit_intent.take_profit_percentage_from_order)}")
        qty = full_position_qty / 100 * take_profit_intent.take_profit_percentage_from_order
        logging.debug(f"qty = {str(qty)}")
        qty = floor_qty(qty, self.__coin_pair_info)
        logging.debug(f"floor qty = {str(qty)}")
        if qty < self.__coin_pair_info.min_qty: raise Exception(f"{qty} is to small")
        return qty
