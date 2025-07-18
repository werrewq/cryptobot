from dataclasses import dataclass

from bot.domain.dto import TradingConfig

@dataclass
class TradeIntent:
    trading_config: TradingConfig
    side: str

@dataclass
class LongIntent(TradeIntent):
    pass

@dataclass
class ShortIntent(TradeIntent):
    pass

@dataclass
class CloseAllIntent(TradeIntent):
    pass

@dataclass
class StopLossIntent(TradeIntent):
    trigger_price: float

@dataclass
class TakeProfitIntent(TradeIntent):
    trigger_price: float
    take_profit_percentage_from_order: int
    market: bool

@dataclass
class RevertLimitIntent(TradeIntent):
    trigger_price: float

@dataclass
class SynchroIntent(TradeIntent):
    pass