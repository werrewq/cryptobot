from Bot.domain.dto.TradeIntent import TradeIntent, LongIntent, ShortIntent
from Bot.domain.dto.TradingConfig import TradingConfig


class SignalToIntentMapper:
    __trading_config: TradingConfig

    def __init__(self, trading_config: TradingConfig):
        self.__trading_config = trading_config

    def map(self, signal) -> TradeIntent:
        buy_or_sell = str(signal["signal"])
        close = float(signal["price"])
        # TODO Доделать заполнение LongIntent и ShortIntent
        # TODO Добавить обработку currency
        currency_name = "BTC"
        match buy_or_sell:
            case "open_long":
                return LongIntent(trading_config=self.__trading_config)
            case "open_short":
                return ShortIntent(trading_config=self.__trading_config)
            case "open_long_when":
                # strategy.entry("Long", strategy.long, when=Timerange())
                pass
            case "open_short_when":
                # strategy.entry("Short", strategy.short, when=Timerange())
                pass
            # strategy.entry("Long",true,when=entry_long)
            # strategy.exit("TP/SL","Long", limit=long_take_level, stop=long_stop_level)
            # strategy.close("Long", when=exit_long, comment="Exit")
            case _:
                raise TypeError('Unsupported trade intent')
