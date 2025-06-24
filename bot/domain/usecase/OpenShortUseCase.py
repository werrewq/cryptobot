from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import ShortIntent
from bot.domain.usecase.CloseLongUseCase import CloseLongUseCase

class OpenShortUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi
    close_long_usecase: CloseLongUseCase

    def __init__(self, broker_api, messenger_api, close_long_usecase):
        self.broker_api = broker_api
        self.messenger_api = messenger_api
        self.close_long_usecase = close_long_usecase

    def run(self, short_intent: ShortIntent):
        self.__bot_open_short(short_intent)

    def __bot_open_short(self, short_intent: ShortIntent):
        self.messenger_api.send_message(message="Пробуем открыть SHORT 📉")
        self.close_long_usecase.run(short_intent)
        message = self.broker_api.place_sell_order(short_intent)
        self.messenger_api.send_message(message="Разместили заказ на продажу\n: " + message)