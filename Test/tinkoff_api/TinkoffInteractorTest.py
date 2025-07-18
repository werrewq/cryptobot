from bot.config.Decrypter import Decrypter
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.tinkoff_api.TinkoffInteractor import TinkoffInteractor
from bot.data.api.tinkoff_api.TinkoffSandboxApi import TinkoffSandboxApi
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent, StopLossIntent, TakeProfitIntent, RevertLimitIntent
from bot.domain.dto.TradingConfig import TradingConfig
from bot.presentation.logger.BotLogger import BotLogger

loger = BotLogger()
loger.run()
trading_config: TradingConfig = TradingConfigProvider().provide(test=True)
decrypter = Decrypter(b'O\xa0\xd3\xe5[m\x8fRWY#\r\x96\xd4\xe7\x9d\x9b\xbe;D\xd4\x00wNA\xe3\xb1o\x8fM\x1c)')
secured_config=SecuredConfig(trading_config=trading_config,decrypter=decrypter)
# tinkoff_api = TinkoffRealApi(secured_config=secured_config)
tinkoff_api = TinkoffSandboxApi(secured_config=secured_config)
tinkoff_interactor = TinkoffInteractor(tinkoff_api=tinkoff_api, secured_config=secured_config, trading_config=trading_config)

def place_sell_order():
    intent = ShortIntent(
        trading_config= trading_config,
        side="Sell"
    )
    res = tinkoff_interactor.place_sell_order(intent)
    print(res)

def have_long_order():
    print(tinkoff_interactor.have_long_position(trading_config))

def have_short_order():
    print(tinkoff_interactor.have_short_position(trading_config))

def close_long_position():
    tinkoff_interactor.close_long_position(trading_config)

def close_short_position():
    tinkoff_interactor.close_short_position(trading_config)

def place_buy_order():
    intent = LongIntent(trading_config, side="Buy")
    res = tinkoff_interactor.place_buy_order(intent)
    print(res)

def set_stop_loss(trigger_price, side = "Sell"):
    intent = StopLossIntent(trading_config, side= side, trigger_price=trigger_price)
    tinkoff_interactor.set_stop_loss(intent)

def cancel_all_orders():
    tinkoff_interactor.cancel_all_active_orders(trading_config)

def set_take_profit(trigger_price, side = "Sell", market = False, take_profit_percentage_from_order = 100):
    intent = TakeProfitIntent(trading_config, side=side, trigger_price=trigger_price, take_profit_percentage_from_order=take_profit_percentage_from_order, market= market)
    tinkoff_interactor.set_take_profit(intent)

def set_revert_limit(trigger_price, side = "Sell"):
    intent = RevertLimitIntent(trading_config, side= side, trigger_price=trigger_price)
    tinkoff_interactor.set_revert_limit(intent)

if __name__ == '__main__':
    place_sell_order()
    set_stop_loss(trigger_price=100, side="Buy")
    close_short_position()
    place_buy_order()
    close_long_position()


    # place_buy_order()
    # set_stop_loss(trigger_price=80, side= "Sell")
    # set_stop_loss(trigger_price=84, side="Sell")
    # set_take_profit(trigger_price=100, side="Sell")
    # set_take_profit(trigger_price=101, side="Sell")
    # close_long_position()
    # place_sell_order()
    # set_stop_loss(trigger_price=100, side= "Buy")
    # set_stop_loss(trigger_price=99, side="Buy")
    # set_take_profit(trigger_price=84, side="Buy")
    # set_take_profit(trigger_price=80, side="Buy")
    # close_short_position()
    # place_buy_order()
    # set_take_profit(trigger_price=101, side="Sell", market=True, take_profit_percentage_from_order=25)
    # set_take_profit(trigger_price=101, side="Sell", market=True, take_profit_percentage_from_order=25)
    # close_long_position()
    # place_sell_order()
    # set_take_profit(trigger_price=101, side="Buy", market=True, take_profit_percentage_from_order=25)
    # set_take_profit(trigger_price=101, side="Buy", market=True, take_profit_percentage_from_order=25)
    # close_short_position()
