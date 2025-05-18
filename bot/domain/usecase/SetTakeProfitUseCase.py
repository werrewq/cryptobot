from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import TakeProfitIntent


class SetTakeProfitUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, take_profit_intent: TakeProfitIntent):
        self.__bot_set_take_profit(take_profit_intent)

    def __bot_set_take_profit(self, take_profit_intent: TakeProfitIntent):
        self.messenger_api.send_message(message="Пробуем закрыть все старые ордера")
        self.broker_api.cancel_all_active_orders(take_profit_intent.trading_config)
        self.messenger_api.send_message(message="Пробуем поставить TAKE PROFIT💰")
        message = self.broker_api.set_take_profit(take_profit_intent)
        self.messenger_api.send_message(message=message)