import logging

from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import ShortIntent

class OpenShortUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, short_intent: ShortIntent):
        self.__bot_open_short(short_intent)

    def __bot_open_short(self, short_intent: ShortIntent):
        logging.debug(f"SHORT UseCase")
        self.messenger_api.send_message(message="Пробуем открыть SHORT 📉")
        message = self.broker_api.place_sell_order(short_intent)
        self.messenger_api.send_message(message="Разместили заказ на продажу\n: " + message)