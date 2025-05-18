import json
import os

from bot.domain.dto.TradingConfig import TradingConfig


class TradingConfigProvider:
    __trading_config_json_file_path = os.path.join(os.path.dirname(__file__), 'trading_config.json')

    def provide(self, test = False) -> TradingConfig:
        trading_config_json = None
        with open(self.__trading_config_json_file_path, 'r') as stream:
            trading_config_json = json.load(stream)
        stream.close()

        if trading_config_json is None:
            raise RuntimeError("TradingConfig was not loaded")
        else:
            test_env_vars = trading_config_json['test_env_vars']
            if test:
                test_env_vars = True
            return TradingConfig(
                order_volume_percent_of_capital = trading_config_json['order_volume_percent_of_capital'],
                target_share_name= trading_config_json['target_share_name'],
                asset_name = trading_config_json['asset_name'],
                leverage = trading_config_json['leverage'],
                test_env_vars = test_env_vars,
                sandbox= trading_config_json['sandbox'],
            )