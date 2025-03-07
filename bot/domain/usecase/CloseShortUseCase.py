from bot.domain import MessengerApi
from bot.domain.BrokerApi import BrokerApi
from bot.domain.dto.TradeIntent import TradeIntent


class CloseShortUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, trade_intent: TradeIntent):
        self.__bot_close_short(trade_intent)

    def __bot_close_short(self, trade_intent: TradeIntent):
        self.broker_api.cancel_all_active_orders(trading_config=trade_intent.trading_config)
        if self.broker_api.have_order_short(trade_intent.trading_config):
            self.broker_api.close_short_position(trade_intent.trading_config)
            self.messenger_api.send_message("#Закрываем SHORT ✅")