from tinkoff.invest import OrderDirection, InstrumentType, StopOrderDirection

from bot.config.TinkoffSecuredConfig import TinkoffSecuredConfig
from bot.data.api.tinkoff_api.Helpers import float_to_quotation
from bot.data.api.tinkoff_api.TinkoffApi import TinkoffApi
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import StopLossIntent, ShortIntent, LongIntent
from bot.domain.dto.TradingConfig import TradingConfig

INSTRUMENT_TYPE = InstrumentType.INSTRUMENT_TYPE_SHARE # TODO вывести в трейдинг конфиг закрыв абстракцией от внутрянки тинька
MONEY_CURRENCY = "rub" # TODO вывести в трейдинг конфиг

class TinkoffInteractor(BrokerApi):
    __tinkoff_api: TinkoffApi
    __account_id: str
    __instrument_figi: str

    def __init__(self, tinkoff_api: TinkoffApi, secured_config: TinkoffSecuredConfig, trading_config: TradingConfig):
        self.__tinkoff_api = tinkoff_api
        self.__account_id = secured_config.get_broker_account_id()
        self.__instrument_figi = self.get_figi(ticker=trading_config.target_coin_name, instrument_type=INSTRUMENT_TYPE)

    def have_order_long(self, trading_config: TradingConfig) -> bool:
        return self.__has_position(direction=OrderDirection.ORDER_DIRECTION_BUY)

    def have_order_short(self, trading_config: TradingConfig) -> bool:
        return self.__has_position(direction=OrderDirection.ORDER_DIRECTION_SELL)

    def __has_position(self, direction: OrderDirection) -> bool:
        positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)

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
        direction: OrderDirection = OrderDirection.ORDER_DIRECTION_SELL
        figi = self.__instrument_figi
        balance = self.get_balance()
        asset_price = self.__tinkoff_api.get_last_price(figi)
        quantity = abs(int(balance.units / asset_price.units.real))
        return self.__place_market_order(direction= direction, quantity=quantity, figi=figi)

    def place_buy_order(self, long_intent: LongIntent) -> str:
        direction = OrderDirection.ORDER_DIRECTION_BUY
        figi = self.__instrument_figi
        balance = self.get_balance()
        asset_price = self.__tinkoff_api.get_last_price(figi)
        quantity = abs(int(balance.units / asset_price.units.real))

        return self.__place_market_order(direction= direction, quantity=quantity, figi=figi)

    def __place_market_order(self, direction: OrderDirection, quantity, figi) -> str:
        resp = self.__tinkoff_api.post_market_order(
            figi=figi,
            quantity=quantity,
            account_id=self.__account_id,
            direction=direction
        )
        return str(resp)

    def get_balance(self):
        account_positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        for money in account_positions.money:
            if money.currency == MONEY_CURRENCY:
                return money
        raise Exception("Не было найдено никаких рублей на аккаунте")

    def get_target_asset_qty_on_account(self):
        account_positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        for asset in account_positions.securities:
            if asset.figi == MONEY_CURRENCY:
                return asset.balance
        raise Exception("Не было найдено никаких ценных бумаг на аккаунте")

    def close_short_position(self, trading_config: TradingConfig):
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
        # Отправляем рыночный ордер на продажу такого же количества в противоположную сторону
        return self.__place_market_order(direction=OrderDirection.ORDER_DIRECTION_BUY, quantity=quantity_to_sell, figi=self.__instrument_figi)

    def close_long_position(self, trading_config: TradingConfig):
        # Получаем портфель
        positions = self.__tinkoff_api.get_positions(account_id=self.__account_id)
        quantity_to_sell = None
        # Ищем позицию по figi
        for position in positions.securities:
            if position.figi == self.__instrument_figi:
                quantity_to_sell = position.balance
        if quantity_to_sell is None:
            raise Exception("Не найдено количество бумаг для закрытия лонга")
        # Отправляем рыночный ордер на продажу такого же количества в противоположную сторону
        return self.__place_market_order(direction=OrderDirection.ORDER_DIRECTION_SELL, quantity=quantity_to_sell, figi=self.__instrument_figi)

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

    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str: # TODO проверить на бою
        orders = self.__tinkoff_api.get_stop_orders(self.__account_id)
        for order in orders.stop_orders:
            self.__tinkoff_api.cancel_stop_order(self.__account_id, stop_order_id=order.stop_order_id)

        direction = None
        if self.have_order_long(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_SELL
        elif self.have_order_short(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_BUY
        if direction is None:
            raise Exception("Не нашли наличия лонгов/шортов для определения направления стоп-лосса")

        stop_price = float_to_quotation(StopLossIntent.trigger_price)

        self.__tinkoff_api.post_stop_loss_order(
            figi=self.__instrument_figi,
            quantity=self.get_target_asset_qty_on_account(),
            direction=direction,
            stop_price=stop_price,
            account_id=self.__account_id,
        )
        return f"Стоп лосс успешно установлен на цене {str(StopLossIntent.trigger_price)}"

    # TODO проверить на бою
    def set_take_profit(self, stop_loss_intent: StopLossIntent) -> str: # TODO StopLossIntent -> TakeProfitIntent
        orders = self.__tinkoff_api.get_stop_orders(self.__account_id)
        for order in orders.stop_orders:
            self.__tinkoff_api.cancel_stop_order(self.__account_id, stop_order_id=order.stop_order_id)

        direction = None
        if self.have_order_long(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_SELL
        elif self.have_order_short(stop_loss_intent.trading_config):
            direction = StopOrderDirection.STOP_ORDER_DIRECTION_BUY
        if direction is None:
            raise Exception("Не нашли наличия лонгов/шортов для определения направления стоп-лосса")

        stop_price = float_to_quotation(StopLossIntent.trigger_price)

        self.__tinkoff_api.post_take_profit_order(
            figi=self.__instrument_figi,
            quantity=self.get_target_asset_qty_on_account(),
            direction=direction,
            stop_price=stop_price,
            account_id=self.__account_id,
        )
        return f"Стоп лосс успешно установлен на цене {str(StopLossIntent.trigger_price)}"