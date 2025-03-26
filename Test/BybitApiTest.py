from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.BybitApi import BybitApi
from bot.domain.dto.TradeIntent import ShortIntent, LongIntent
from bot.domain.dto.TradingConfig import TradingConfig

trading_config: TradingConfig = TradingConfigProvider().provide()
api = BybitApi(trading_config)

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
    api.get_assets(trading_config.asset_name)

def place_buy_order():
    intent = LongIntent(trading_config, side="buy")
    api.place_buy_order(intent)

def get_filters():
    api.get_filters(trading_config)

if __name__ == '__main__':
    close_short_position()


