from Bot.data.api.BybitApi import BybitApi
from Bot.domain.TradeIntent import ShortIntent, LongIntent

api = BybitApi()
currency_name="SOL"

def place_sell_order():
    intent = ShortIntent(
        currency_name=currency_name,
        message="sell"
    )
    api.place_sell_order(intent)

def have_long_order():
    print(api.have_order_long(currency_name))

def have_short_order():
    print(api.have_order_short(currency_name))

def close_long_position():
    api.close_long_position(currency_name)

def get_assets():
    api.get_assets(currency_name)

def place_buy_order():
    intent = LongIntent(currency_name= currency_name, message= "long")
    api.place_buy_order(intent)

if __name__ == '__main__':
    close_long_position()


