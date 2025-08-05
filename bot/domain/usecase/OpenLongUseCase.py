import logging

from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import LongIntent


class OpenLongUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, long_intent: LongIntent):
        self.__bot_open_long(long_intent)


    def __bot_open_long(self, long_intent: LongIntent):
        logging.debug(f"LONG UseCase")
        self.messenger_api.send_message(message="Пробуем закрыть все старые стоп ордера")
        self.broker_api.cancel_all_active_orders(long_intent.trading_config)
        self.messenger_api.send_message(message="Пробуем открыть LONG 📈")
        message = self.broker_api.place_buy_order(long_intent)
        self.messenger_api.send_message(message="Разместили заказ на покупку\n" + message)