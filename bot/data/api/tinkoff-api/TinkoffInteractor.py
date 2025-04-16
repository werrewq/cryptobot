from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import StopLossIntent, ShortIntent, LongIntent
from bot.domain.dto.TradingConfig import TradingConfig


class TinkoffInteractor(BrokerApi):

    def have_order_long(self, trading_config: TradingConfig) -> bool:
        pass

    def have_order_short(self, trading_config: TradingConfig) -> bool:
        pass

    def place_buy_order(self, long_intent: LongIntent) -> str:
        pass

    def place_sell_order(self, short_intent: ShortIntent) -> str:
        pass

    def close_short_position(self, trading_config: TradingConfig):
        pass

    def close_long_position(self, trading_config: TradingConfig):
        pass

    def cancel_all_active_orders(self, trading_config: TradingConfig):
        pass

    def set_stop_loss(self, stop_loss_intent: StopLossIntent) -> str:
        pass