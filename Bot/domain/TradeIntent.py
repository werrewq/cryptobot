from dataclasses import dataclass

@dataclass
class TradeIntent:
    currency_name: str


@dataclass
class LongIntent(TradeIntent):
    message: str

@dataclass
class ShortIntent(TradeIntent):
    message: str