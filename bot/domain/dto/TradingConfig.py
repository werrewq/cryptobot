from dataclasses import dataclass

@dataclass
class TradingConfig:
    order_volume_percent_of_capital: int
    target_share_name: str
    asset_name: str
    leverage: int
    sandbox: bool
    test_env_vars: bool

