from Test.MessengerApiMock import MessengerApiMock
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.BybitApi import BybitApi
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.TradingLogger import TradingLogger

trading_config: TradingConfig = TradingConfigProvider().provide(test=True)
retry_request_handler_fabric = RetryRequestHandlerFabric(MessengerApiMock())

api = BybitApi(trading_config, TradingLogger(), SecuredConfig(trading_config), retry_request_handler_fabric)

def place_sell_order():
    intent = ShortIntent(
        trading_config= trading_config,
        side="sell"
    )
    api.place_sell_order(intent)

def have_long_order():
    print(api.have_order_long(trading_config))

def have_short_order():
    print(api.have_order_short(trading_config))

def close_long_position():
    api.close_long_position(trading_config)

def close_short_position():
    api.close_short_position(trading_config)

def get_assets():
    print(str(api.get_assets(trading_config.asset_name)))

def place_buy_order():
    intent = LongIntent(trading_config, side="buy")
    res = api.place_buy_order(intent)
    print(res)

def get_filters():
    api.get_filters(trading_config)

if __name__ == '__main__':
    get_assets()


