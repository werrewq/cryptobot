from dataclasses import dataclass

from bot.domain.dto import TradingConfig

@dataclass
class TradeIntent:
    trading_config: TradingConfig

@dataclass
class LongIntent(TradeIntent):
    pass

@dataclass
class ShortIntent(TradeIntent):
    pass