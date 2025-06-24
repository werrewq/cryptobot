import abc

from bot.domain.dto.TradeIntent import LongIntent, ShortIntent, StopLossIntent, TakeProfitIntent
from bot.domain.dto.TradingConfig import TradingConfig


class BrokerApi:

    @abc.abstractmethod
    def have_long_position(self, trading_config: TradingConfig) -> bool:
        pass

    @abc.abstractmethod
    def have_short_position(self, trading_config: TradingConfig) -> bool:
        pass

    @abc.abstractmethod
    def place_buy_order(self, long_intent: LongIntent) -> str:
        pass

    @abc.abstractmethod
    def place_sell_order(self, short_intent: ShortIntent) -> str:
        pass

    @abc.abstractmethod
    def close_short_position(self, trading_config: TradingConfig) -> str:
        pass

    @abc.abstractmethod
    def close_long_position(self, trading_config: TradingConfig) -> str:
        pass

    @abc.abstractmethod
    def cancel_all_active_orders(self, trading_config: TradingConfig):
        pass

    @abc.abstractmethod
    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        pass

    @abc.abstractmethod
    def set_take_profit(self, take_profit_intent: TakeProfitIntent) -> str:
        pass