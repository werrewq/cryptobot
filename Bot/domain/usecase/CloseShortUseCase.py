from Bot.domain import MessengerApi
from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.TradeIntent import TradeIntent


class CloseShortUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, trade_intent: TradeIntent):
        try:
            self.__bot_close_short(trade_intent)
        except Exception as e:
            print(repr(e))
            self.messenger_api.send_message(message="Ошибка во время закрытия Шорта: " + repr(e))

    def __bot_close_short(self, trade_intent: TradeIntent):
        if self.broker_api.have_order_short(trade_intent.currency_name):
            self.broker_api.close_short_position(trade_intent.currency_name)
            self.messenger_api.send_message("#Закрываем SHORT ✅")