import abc

from Bot.domain.TradeIntent import LongIntent, ShortIntent


class BrokerApi:

    @abc.abstractmethod
    def have_order_long(self, currency_name) -> bool:
        pass

    @abc.abstractmethod
    def have_order_short(self, currency_name) -> bool:
        pass

    @abc.abstractmethod
    def place_buy_order(self, long_intent: LongIntent) -> str:
        pass

    @abc.abstractmethod
    def place_sell_order(self, short_intent: ShortIntent) -> str:
        pass

    @abc.abstractmethod
    def close_short_position(self, currency_name):
        pass

    @abc.abstractmethod
    def close_long_position(self, currency_name):
        pass

    @abc.abstractmethod
    def cancel_all_active_orders(self):
        pass