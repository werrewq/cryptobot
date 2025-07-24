import logging
from time import sleep

from tinkoff.invest import OrderDirection, InstrumentType, StopOrderDirection, GetMaxLotsResponse

from bot.config.SecuredConfig import SecuredConfig
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.data.api.tinkoff_api.Helpers import float_to_quotation
from bot.data.api.tinkoff_api.TinkoffApi import TinkoffApi
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import StopLossIntent, ShortIntent, LongIntent, TakeProfitIntent, RevertLimitIntent
from bot.domain.dto.TradingConfig import TradingConfig

INSTRUMENT_TYPE = InstrumentType.INSTRUMENT_TYPE_SHARE # TODO вывести в трейдинг конфиг, закрыв абстракцией от внутрянки тинька
MONEY_CURRENCY = "rub" # TODO вывести в трейдинг конфиг

class TinkoffInteractor(BrokerApi):
    __tinkoff_api: TinkoffApi
    __account_id: str
    __instrument_figi: str
    __trading_config: TradingConfig
    __retry_request_fabric: RetryRequestHandlerFabric

    def __init__(
            self,
            tinkoff_api: TinkoffApi,
            secured_config: SecuredConfig,
            trading_config: TradingConfig,
            retry_request_fabric: RetryRequestHandlerFabric,
    ):
        self.__tinkoff_api = tinkoff_api
        self.__account_id = secured_config.get_broker_account_id()
        self.__trading_config = trading_config
        self.__retry_request_fabric = retry_request_fabric
        self.__instrument_figi = self.get_figi(ticker=trading_config.target_share_name, instrument_type=INSTRUMENT_TYPE)

    def have_long_position(self, trading_config: TradingConfig) -> bool:
        return self.__has_position(direction=OrderDirection.ORDER_DIRECTION_BUY)

    def have_short_position(self, trading_config: TradingConfig) -> bool:
        return self.__has_position(direction=OrderDirection.ORDER_DIRECTION_SELL)

    def __has_position(self, direction: OrderDirection) -> bool:
        positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        logging.debug(f"__has_position:\n {str(positions)}")

        for position in positions.securities:
            if position.figi == self.__instrument_figi:
                if direction is OrderDirection.ORDER_DIRECTION_BUY:
                    if position.balance > 0:
                        return True
                if direction is OrderDirection.ORDER_DIRECTION_SELL:
                    if position.balance < 0:
                        return True
                # quantity - количество лотов в портфеле
                # Если quantity > 0 — значит есть лонг позиция
                # Если quantity < 0 — значит есть шорт позиция
        return False

    def place_sell_order(self, short_intent: ShortIntent) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda : self.__place_sell_order(short_intent))

    def __place_sell_order(self, short_intent: ShortIntent) -> str:
        direction: OrderDirection = OrderDirection.ORDER_DIRECTION_SELL
        figi = self.__instrument_figi
        if self.have_long_position(short_intent.trading_config):
            long_quantity = self.get_target_asset_qty_on_account()
            quantity = long_quantity * 2
            logging.debug(f"place_sell_order: quantity = {str(quantity)} get_target_asset_qty_on_account = {str(long_quantity)}")
        else:
            max_market_lots = self.get_max_market_lots()
            quantity = max_market_lots * self.__trading_config.order_volume_percent_of_capital / 100
            logging.debug(f"place_sell_order: quantity = {str(quantity)} buy_max_market_lots = {str(max_market_lots)}")
        return self.__place_market_order(direction=direction, quantity=int(quantity), figi=figi)

    def place_buy_order(self, long_intent: LongIntent) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__place_buy_order(long_intent))

    def __place_buy_order(self, long_intent: LongIntent) -> str:
        direction = OrderDirection.ORDER_DIRECTION_BUY
        figi = self.__instrument_figi
        max_market_lots = self.get_max_market_lots()
        quantity = max_market_lots * self.__trading_config.order_volume_percent_of_capital / 100
        # if self.have_short_position(long_intent.trading_config):
        #     quantity = quantity * 2
        logging.debug(f"place_buy_order: quantity = {str(quantity)} buy_max_market_lots = {str(max_market_lots)}")
        return self.__place_market_order(direction= direction, quantity=int(quantity), figi=figi)

    def __place_market_order(self, direction: OrderDirection, quantity, figi) -> str:
        resp = self.__tinkoff_api.post_market_order(
            figi=figi,
            quantity=quantity,
            account_id=self.__account_id,
            direction=direction
        )
        balance = self.get_balance()
        order_message = f'''Тип сделки: Market\nБумага: {self.__trading_config.target_share_name}\nНаправление: {str(direction.value)}\n Сумма заказа: {str(resp.total_order_amount.units)}\n Цена одной акции: {str(resp.executed_order_price.units)}\n Баланс на кошельке: {str(balance.units)}'''
        return order_message

    def get_balance(self):
        account_positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        for money in account_positions.money:
            if money.currency == MONEY_CURRENCY:
                return money
        raise Exception("Не было найдено никаких рублей на аккаунте")

    def get_target_asset_qty_on_account(self):
        account_positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        for asset in account_positions.securities:
            if asset.figi == self.__instrument_figi:
                return abs(asset.balance)
        raise Exception("Не было найдено никаких ценных бумаг на аккаунте")

    def close_short_position(self, trading_config: TradingConfig) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__close_short_position(trading_config))

    def __close_short_position(self, trading_config: TradingConfig) -> str:
        # Получаем портфель
        positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        quantity_to_sell = None
        # Ищем позицию по figi
        for position in positions.securities:
            if position.figi == self.__instrument_figi:
                quantity_to_sell = position.balance
        if quantity_to_sell is None:
            raise Exception("Не найдено количество бумаг для закрытия шорта")
        quantity_to_sell = abs(quantity_to_sell)
        logging.debug(f"CLOSE SHORT: quantity = {str(quantity_to_sell)}")
        # Отправляем рыночный ордер на продажу такого же количества в противоположную сторону
        res = self.__place_market_order(direction=OrderDirection.ORDER_DIRECTION_BUY, quantity=quantity_to_sell, figi=self.__instrument_figi)
        while self.have_short_position(trading_config) or self.__tinkoff_api.have_active_orders():
            logging.debug("close_short_position sleep")
            sleep(2)
        return res

    def close_long_position(self, trading_config: TradingConfig) -> str:
        retry_handler = self.__retry_request_fabric.create(request_limit=3)
        return retry_handler.handle(lambda: self.__close_long_position(trading_config))

    def __close_long_position(self, trading_config: TradingConfig) -> str:
        # Получаем портфель
        positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        quantity_to_sell = None
        # Ищем позицию по figi
        for position in positions.securities:
            if position.figi == self.__instrument_figi:
                quantity_to_sell = position.balance
        if quantity_to_sell is None:
            raise Exception("Не найдено количество бумаг для закрытия лонга")
        logging.debug(f"CLOSE LONG: quantity = {str(quantity_to_sell)}")
        # Отправляем рыночный ордер на продажу такого же количества в противоположную сторону
        res = self.__place_market_order(direction=OrderDirection.ORDER_DIRECTION_SELL, quantity=quantity_to_sell, figi=self.__instrument_figi)
        while self.have_long_position(trading_config) or self.__tinkoff_api.have_active_orders():
            logging.debug("close_long_position sleep")
            sleep(2)
        return res


    def cancel_all_active_orders(self, trading_config: TradingConfig):
        self.__tinkoff_api.cancel_all_orders()

    def get_figi(self, ticker, instrument_type: InstrumentType) -> str:
        instruments = self.__tinkoff_api.find_instruments_by_ticker(ticker, instrument_type=instrument_type)
        figi = None
        for instrument in instruments:
            if instrument.ticker == ticker:
                figi = instrument.figi
                break
        if figi is None:
            raise Exception("Не нашли figi инструмента на бирже")
        return figi

    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        orders = self.__tinkoff_api.get_stop_orders(self.__account_id)
        for order in orders.stop_orders:
            self.__tinkoff_api.cancel_stop_order(self.__account_id, stop_order_id=order.stop_order_id)

        direction = None
        if self.have_long_position(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_SELL
        elif self.have_short_position(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_BUY
        if direction is None:
            raise Exception("Не нашли наличия лонгов/шортов для определения направления стоп-лосса")

        if (stop_loss_intent.side == "Sell" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_BUY) or (stop_loss_intent.side == "Buy" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_SELL):
            raise Exception(f"Не правильное направление Stop Loss: side=={stop_loss_intent.side}, а  StopOrderDirection=={direction.name}")

        stop_price = float_to_quotation(stop_loss_intent.trigger_price)

        self.__tinkoff_api.post_stop_loss_order( # TODO нужно возвращать какой-то пруф от api
            figi=self.__instrument_figi,
            quantity=self.get_target_asset_qty_on_account(),
            direction=direction,
            stop_price=stop_price,
            account_id=self.__account_id,
        )
        return f"Стоп лосс успешно установлен на цене {str(stop_loss_intent.trigger_price)}"

    def set_take_profit(self, take_profit_intent: TakeProfitIntent) -> str:

        orders = self.__tinkoff_api.get_stop_orders(self.__account_id)
        for order in orders.stop_orders:
            self.__tinkoff_api.cancel_stop_order(self.__account_id, stop_order_id=order.stop_order_id)
        direction = None
        if self.have_long_position(take_profit_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_SELL
        elif self.have_short_position(take_profit_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_BUY
        if direction is None:
            raise Exception("Не нашли наличия лонгов/шортов для определения направления стоп-лосса")

        qty_to_close = int(self.get_target_asset_qty_on_account() * take_profit_intent.take_profit_percentage_from_order / 100)

        logging.debug(f"Tinkoff interactor set_take_profit.market: = {str(take_profit_intent.market)}")
        if take_profit_intent.market:
            return self.__set_market_take_profit(direction, qty_to_close)

        stop_price = float_to_quotation(take_profit_intent.trigger_price)

        if (take_profit_intent.side == "Sell" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_BUY) or (take_profit_intent.side == "Buy" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_SELL):
            raise Exception(f"Не правильное направление Take Profit: side=={take_profit_intent.side}, а  StopOrderDirection=={direction.name}")

        self.__tinkoff_api.post_take_profit_order(
            figi=self.__instrument_figi,
            quantity=qty_to_close,
            direction=direction,
            stop_price=stop_price,
            account_id=self.__account_id,
        )
        return f"Take profit успешно установлен на цене {str(take_profit_intent.trigger_price)}"

    def __set_market_take_profit(self, direction, qty_to_close):
        if direction is StopOrderDirection.STOP_ORDER_DIRECTION_SELL:
            direction = OrderDirection.ORDER_DIRECTION_SELL
        else:
            direction = OrderDirection.ORDER_DIRECTION_BUY
        resp = self.__place_market_order(direction=direction, quantity=qty_to_close, figi=self.__instrument_figi)
        return f"Take profit по маркету успешно выполнен.\n {resp}"

    def get_max_market_lots(self) -> int:
        res = self.__tinkoff_api.get_max_market_lots(account_id=self.__account_id, figi=self.__instrument_figi)
        buy_max_lots = res.buy_limits.buy_max_lots
        margin_buy_max_market_lots = res.buy_margin_limits.buy_max_market_lots
        buy_max_market_lots = res.buy_limits.buy_max_market_lots
        logging.debug(f"get_max_market_lots:\n{str(res)}")
        # TODO обрабатываем странное поведение API buy_max_lots=8 при buy_max_market_lots=0
        # GetMaxLotsResponse(
        #     currency='RUB',
        #     buy_limits=BuyLimitsView(
        #         buy_money_amount=Quotation(units=28952, nano=0),
        #         buy_max_lots=8,
        #         buy_max_market_lots=0
        #     ),
        #     buy_margin_limits=BuyLimitsView(
        #         buy_money_amount=Quotation(units=231616, nano=0),
        #         buy_max_lots=69,
        #         buy_max_market_lots=68),
        #     sell_limits=SellLimitsView(sell_max_lots=0),
        #     sell_margin_limits=SellLimitsView(sell_max_lots=43)
        # )
        if buy_max_market_lots == 0 and buy_max_lots > 0 and margin_buy_max_market_lots > 0:
            logging.debug(f"Ошибка API:\n  buy_max_market_lots == 0 and buy_max_lots > 0 and margin_buy_max_market_lots > 0")
            return buy_max_lots
        else:
            return buy_max_market_lots

    def set_revert_limit(self, revert_limit_intent: RevertLimitIntent) -> str:
        orders = self.__tinkoff_api.get_stop_orders(self.__account_id)
        for order in orders.stop_orders:
            self.__tinkoff_api.cancel_stop_order(self.__account_id, stop_order_id=order.stop_order_id)

        direction = None
        if self.have_long_position(revert_limit_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_SELL
        elif self.have_short_position(revert_limit_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_BUY
        if direction is None:
            raise Exception("Не нашли наличия лонгов/шортов для определения направления стоп-лосса")

        if (revert_limit_intent.side == "Sell" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_BUY) or (
                revert_limit_intent.side == "Buy" and direction is StopOrderDirection.STOP_ORDER_DIRECTION_SELL):
            raise Exception(
                f"Не правильное направление Revert Limit: side=={revert_limit_intent.side}, а  StopOrderDirection=={direction.name}")

        stop_price = float_to_quotation(revert_limit_intent.trigger_price)
        revert_qty = int(self.get_target_asset_qty_on_account() * 2)

        self.__tinkoff_api.post_stop_loss_order(
            figi=self.__instrument_figi,
            quantity=revert_qty,
            direction=direction,
            stop_price=stop_price,
            account_id=self.__account_id,
        )
        return f"Стоп лосс успешно установлен на цене {str(revert_limit_intent.trigger_price)}"
