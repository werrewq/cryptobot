from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import StopLossIntent


class SetStopLossUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, stop_loss_intent: StopLossIntent):
        self.__bot_set_stop_loss(stop_loss_intent)

    def __bot_set_stop_loss(self, stop_loss_intent: StopLossIntent):
        self.messenger_api.send_message(message="Пробуем закрыть все старые ордера")
        self.broker_api.cancel_all_active_orders(stop_loss_intent.trading_config)
        self.messenger_api.send_message(message="Пробуем поставить STOP LOSS ⛔")
        message = self.broker_api.set_stop_loss(stop_loss_intent)
        self.messenger_api.send_message(message=message)