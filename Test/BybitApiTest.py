from Test.MessengerApiMock import MessengerApiMock
from bot.config.Decrypter import Decrypter
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.BybitApi import BybitApi
from bot.data.api.BybitInteractor import BybitInteractor
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent, StopLossIntent, TakeProfitIntent
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.BotLogger import BotLogger
from bot.presentation.logger.TradingLogger import TradingLogger

loger = BotLogger()
loger.run()
trading_config: TradingConfig = TradingConfigProvider().provide(test=True)
retry_request_handler_fabric = RetryRequestHandlerFabric(MessengerApiMock())
decrypter = Decrypter(b'\xda\xff\x84\xceVQ\nr(\x99?\x8b\x074\x05\x1a\xb0\x99\x95\x14z\x96\xd0\n\xf9dB\xa4\xd5j\xcd\xfd')
bybit_api = BybitApi(trading_config, SecuredConfig(trading_config, decrypter = decrypter))
api = BybitInteractor(
    bybit_api= bybit_api,
    retry_request_fabric= retry_request_handler_fabric,
    trading_logger= TradingLogger(),
    trading_config= trading_config
)

def place_sell_order():
    intent = ShortIntent(
        trading_config= trading_config,
        side="sell"
    )
    res = api.place_sell_order(intent)
    print(res)

def have_long_order():
    print(api.have_long_position(trading_config))

def have_short_order():
    print(api.have_short_position(trading_config))

def close_long_position():
    api.close_long_position(trading_config)

def close_short_position():
    api.close_short_position(trading_config)

def get_assets():
    print(str(api.get_total_available_balance(trading_config.asset_name)))

def place_buy_order():
    intent = LongIntent(trading_config, side="buy")
    res = api.place_buy_order(intent)
    print(res)

def get_filters():
    api.get_filters(trading_config)

def set_stop_loss():
    intent = StopLossIntent(trading_config, side= "Sell", trigger_price=115)
    api.set_stop_loss(intent)

def set_take_profit():
    intent = TakeProfitIntent(trading_config, side= "Buy", trigger_price=115, take_profit_percentage_from_order=25, market=False)
    api.set_take_profit(intent)

def cancel_all_orders():
    api.cancel_all_active_orders(trading_config)

if __name__ == '__main__':
    get_filters()


