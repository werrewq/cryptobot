from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.Websocket.BybitWebsocket import BybitWebsocket
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.BotLogger import BotLogger

trading_config: TradingConfig = TradingConfig(
    order_volume_percent_of_capital=10,
    target_coin_name="SOL",
    asset_name="USDT",
    leverage=1,
    testnet=False,
    demo=True,
    test_env_vars=True,
)
secured_config: SecuredConfig = SecuredConfig(trading_config)
logger: BotLogger = BotLogger()
logger.run()

def subscribe_to_ticker():
    ws = BybitWebsocket(secured_config=secured_config, trading_config=trading_config, channel_type="linear")
    ws.subscribe_to_ticker()

def subscribe_to_wallet():
    ws = BybitWebsocket(secured_config=secured_config, trading_config=trading_config, channel_type="private")
    ws.subscribe_to_wallet()

if __name__ == '__main__':
    subscribe_to_wallet()