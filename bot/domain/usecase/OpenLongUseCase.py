from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import LongIntent
from bot.domain.usecase.CloseShortUseCase import CloseShortUseCase


class OpenLongUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi
    close_short_usecase: CloseShortUseCase

    def __init__(self, broker_api, messenger_api, close_short_usecase):
        self.broker_api = broker_api
        self.messenger_api = messenger_api
        self.close_short_usecase = close_short_usecase

    def run(self, long_intent: LongIntent):
        self.__bot_open_long(long_intent)


    def __bot_open_long(self, long_intent: LongIntent):
        self.messenger_api.send_message(message="Пробуем открыть LONG 📈")
        self.close_short_usecase.run(long_intent)
        message = self.broker_api.place_buy_order(long_intent)
        self.messenger_api.send_message(message="Разместили заказ на покупку" + message)

    # async def bot_open_long(message, api, close):
    #     try:
    #         # if api.have_order_short(name_coin_u):
    #         #     api.close_position(name_coin_u, "Buy", 1)
    #         #     bot_u.send_message(message.chat.id, "#Close SHORT ✅")
    #         bot_u.send_message(message.chat.id, str(api.place_order(name_coin_u, "Buy", 10)))
    #         bot_u.send_message(message.chat.id, "#Open LONG 📈")
    #         bot_u.send_message(message.chat.id, str(api.get_equity("USDT")))
    #
    #         qty_long = api.get_position_qty(name_coin_u + "USDT", 0)
    #         part1 = round(qty_long * 0.1, 4)
    #         price1 = round(close * 1.05, 4)
    #         price2 = round(close * 1.1, 4)
    #         price3 = round(close * 1.15, 4)
    #         price4 = round(close * 1.2, 4)
    #         price5 = round(close * 1.25, 4)
    #         price6 = round(close * 1.3, 4)
    #         price7 = round(close * 1.35, 4)
    #         api.set_tp_qty(name_coin_u, "Buy", price1, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price2, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price3, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price4, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price5, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price6, part1)
    #         api.set_tp_qty(name_coin_u, "Buy", price7, part1)
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
    #             await bot_open_long(message, api_u, close)
    #
    #     count_ex = 0