import logging

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
        logging.debug(f"LONG UseCase")
        self.messenger_api.send_message(message="Пробуем открыть LONG 📈")
        self.close_short_usecase.run(long_intent)
        message = self.broker_api.place_buy_order(long_intent)
        self.messenger_api.send_message(message="Разместили заказ на покупку\n" + message)