from dataclasses import dataclass

@dataclass
class TradingConfig:
    order_volume_percent_of_capital: int
    target_coin_name: str
    asset_name: str
    testnet: bool
