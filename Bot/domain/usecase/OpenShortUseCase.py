from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.MessengerApi import MessengerApi
from Bot.domain.TradeIntent import ShortIntent
from Bot.domain.usecase.CloseLongUseCase import CloseLongUseCase

class OpenShortUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi
    close_long_usecase: CloseLongUseCase

    def __init__(self, broker_api, messenger_api, close_long_usecase):
        self.broker_api = broker_api
        self.messenger_api = messenger_api
        self.close_long_usecase = close_long_usecase

    def run(self, short_intent: ShortIntent):
        try:
            self.__bot_open_short(short_intent)
        except Exception as e:
            print(repr(e))
            self.messenger_api.send_message(message="Ошибка во время открытия Шорта: " + repr(e))

    def __bot_open_short(self, short_intent: ShortIntent):
        self.messenger_api.send_message(message="Пробуем открыть SHORT 📉")
        self.close_long_usecase.run(short_intent)
        message = self.broker_api.place_sell_order(short_intent)
        self.messenger_api.send_message(message="Разместили заказ на покупку: " + message)

    #
    # async def bot_open_short(message, api, close):
    #     try:
    #         if api.have_order_long(name_coin_u):
    #             api.close_position(name_coin_u, "Sell", 0)
    #             bot_u.send_message(message.chat.id, "#Close LONG ✅")
    #         bot_u.send_message(message.chat.id, str(api.place_order(name_coin_u, "Sell", 10)))
    #         bot_u.send_message(message.chat.id, "#Open SHORT 📉")
    #         bot_u.send_message(message.chat.id, str(api.get_equity("USDT")))
    #
    #         qty_short = api.get_position_qty(name_coin_u + "USDT", 1)
    #         part1 = round(qty_short * 0.1, 4)
    #         price1 = round(close * 0.95, 4)
    #         price2 = round(close * 0.9, 4)
    #         price3 = round(close * 0.85, 4)
    #         price4 = round(close * 0.8, 4)
    #         price5 = round(close * 0.75, 4)
    #         price6 = round(close * 0.7, 4)
    #         price7 = round(close * 0.65, 4)
    #         api.set_tp_qty(name_coin_u, "Sell", price1, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price2, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price3, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price4, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price5, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price6, part1)
    #         api.set_tp_qty(name_coin_u, "Sell", price7, part1)
    #         bot_u.send_message(message.chat.id, "Set TakeProfits ✅")
    #
    #     except Exception as e:
    #         global count_ex, api_key_u, api_secret_u, api_u
    #         if count_ex == 1:
    #             global api_u
    #             api_u = None
    #             bot_u.send_message(message.chat.id, "❗️BOT STOPPED❗️ \n" +
    #                                "SOMETHING SERIOUS HAPPENED")
    #             bot_u.send_message(message.chat.id, "🚫")
    #         else:
    #             bot_u.send_message(message.chat.id, e.__str__())
    #             api_u = Api(api_key_u, api_secret_u)
    #             bot_u.send_message(message.chat.id, "Recreate API")
    #             count_ex = count_ex + 1
    #             # await
    #             await bot_open_short(message, api_u, close)
    #
    #     count_ex = 0
