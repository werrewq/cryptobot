from bot.domain.dto.TradeIntent import TradeIntent, LongIntent, ShortIntent
from bot.domain.dto.TradingConfig import TradingConfig


class SignalToIntentMapper:
    __trading_config: TradingConfig

    def __init__(self, trading_config: TradingConfig):
        self.__trading_config = trading_config

    def map(self, signal) -> TradeIntent:
        buy_or_sell = str(signal["signal"])
        # TODO Доделать заполнение LongIntent и ShortIntent
        # TODO Добавить обработку currency
        currency_name = "BTC"
        match buy_or_sell:
            case "open_long":
                return LongIntent(trading_config=self.__trading_config)
            case "open_short":
                return ShortIntent(trading_config=self.__trading_config)
            # strategy.entry("Long",true,when=entry_long)
            # strategy.exit("TP/SL","Long", limit=long_take_level, stop=long_stop_level)
            # strategy.close("Long", when=exit_long, comment="Exit")
            case _:
                raise TypeError('Unsupported trade intent')
