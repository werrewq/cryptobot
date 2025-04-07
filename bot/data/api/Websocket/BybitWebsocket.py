from time import sleep

from pybit.unified_trading import WebSocket

from bot.config.SecuredConfig import SecuredConfig
from bot.domain.dto.TradingConfig import TradingConfig

MARKET_CATEGORY = "linear"

class BybitWebsocket:
    __websocket: WebSocket
    __trading_config: TradingConfig

    def __init__(
            self,
            secured_config: SecuredConfig,
            trading_config: TradingConfig,
            channel_type: str
    ):
        self.__trading_config = trading_config
        self.__websocket = WebSocket(
            demo=trading_config.demo,
            testnet=trading_config.testnet,
            channel_type=channel_type,
            api_key=secured_config.get_broker_api_key(),
            api_secret=secured_config.get_broker_secret_key(),
            callback_function=self.handle_message
        )

    def handle_message(self, m):
        print(str(m))

    def subscribe_to_ticker(self):
        """
        Подписка на каналы на все торгуемую пару,
        :param ws:
        :return:
        """
        symbol = self.__trading_config.target_coin_name + self.__trading_config.asset_name

        self.__websocket.ticker_stream(symbol=symbol, callback=handle_ticker)

    def subscribe_to_wallet(self):
        self.__websocket.wallet_stream(callback=handle_wallet)
        while True:
            sleep(1)

def handle_ticker(m):
    print(str(m))
    d = m.get('data', {})
    print(d['symbol'], d['lastPrice'], sep=":")

def handle_wallet(m):
    print(str(m))
