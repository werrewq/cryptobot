from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import CloseAllIntent


class CloseAllUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, close_all_intent: CloseAllIntent):
        self.__bot_close_all(close_all_intent)

    def __bot_close_all(self, close_all_intent: CloseAllIntent):
        self.broker_api.cancel_all_active_orders(trading_config=close_all_intent.trading_config)
        self.messenger_api.send_message("#Закрываем все ордера")
        if self.broker_api.have_long_position(close_all_intent.trading_config):
            self.messenger_api.send_message("#Закрываем Long")
            resp = self.broker_api.close_long_position(close_all_intent.trading_config)
            self.messenger_api.send_message("#Закрыли Long ✅\n" + resp)
        if self.broker_api.have_short_position(close_all_intent.trading_config):
            self.messenger_api.send_message("#Закрываем SHORT")
            resp = self.broker_api.close_short_position(close_all_intent.trading_config)
            self.messenger_api.send_message("#Закрыли SHORT ✅\n" + resp)
