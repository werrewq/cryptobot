import logging

from bot.domain.dto.TradeIntent import TradeIntent, LongIntent, ShortIntent, StopLossIntent, TakeProfitIntent, \
    CloseAllIntent, RevertLimitIntent, SynchroIntent
from bot.domain.dto.TradingConfig import TradingConfig

# {"signal":"{{strategy.order.comment}}","token":"2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2","side":"{{strategy.order.action}}"}
class SignalToIntentMapper:
    __trading_config: TradingConfig

    def __init__(self, trading_config: TradingConfig):
        self.__trading_config = trading_config

    def map(self, data) -> TradeIntent:
        buy_or_sell = str(data["signal"])
        match buy_or_sell:
            case "open_long":
                return LongIntent(trading_config=self.__trading_config, side="Buy")
            case "open_short":
                return ShortIntent(trading_config=self.__trading_config, side="Sell")
            case "stop_loss":
                return StopLossIntent(trading_config=self.__trading_config, trigger_price= float(data["stop_price"]), side=data["side"])
            case "take_profit":
                take_profit_percentage = int(data["take_profit_percentage_from_order"]) if "take_profit_percentage_from_order" in data else 100
                market = bool(data["market"]) if "market" in data else False
                logging.debug(f"Signal mapper market = {str(market)}")
                return TakeProfitIntent(
                    trading_config=self.__trading_config,
                    trigger_price=float(data["trigger_price"]),
                    take_profit_percentage_from_order=take_profit_percentage,
                    market=market,
                    side=data["side"])
            case "revert_limit":
                return RevertLimitIntent(trading_config=self.__trading_config, trigger_price=float(data["stop_price"]),
                                      side=data["side"])
            case "close_all":
                return CloseAllIntent(trading_config=self.__trading_config, side="all")
            case "synchro":
                return SynchroIntent(trading_config=self.__trading_config, side=data["side"])
            case _:
                raise TypeError('Unsupported trade intent')
