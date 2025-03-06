import json
import os

from Bot.domain.dto.TradingConfig import TradingConfig


class TradingConfigProvider:
    __trading_config_json_file_path = os.path.join('..', 'Bot', 'config', 'trading_config.json')

    def provide(self) -> TradingConfig:
        trading_config_json = None
        with open(self.__trading_config_json_file_path, 'r') as stream:
            trading_config_json = json.load(stream)
        stream.close()

        if trading_config_json is None:
            raise RuntimeError("TradingConfig was not loaded")
        else:
            return TradingConfig(
                order_volume_percent_of_capital = trading_config_json['order_volume_percent_of_capital'],
                target_coin_name = trading_config_json['target_coin_name'],
                asset_name = trading_config_json['asset_name'],
                testnet = trading_config_json['testnet'],
            )