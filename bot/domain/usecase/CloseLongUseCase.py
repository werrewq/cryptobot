from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import TradeIntent


class CloseLongUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, trade_intent: TradeIntent):
        self.__bot_close_long(trade_intent)

    def __bot_close_long(self, trade_intent: TradeIntent):
        self.broker_api.cancel_all_active_orders(trading_config=trade_intent.trading_config)
        has_long = self.broker_api.have_order_long(trade_intent.trading_config)
        self.messenger_api.send_message(f"#Проверяем наличие открытых лонгов: {str(has_long)}")
        if has_long:
            self.messenger_api.send_message("#Закрываем Long")
            resp = self.broker_api.close_long_position(trade_intent.trading_config)
            self.messenger_api.send_message("#Закрыли Long ✅\n" + resp)