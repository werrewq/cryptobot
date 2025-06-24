import logging

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
        logging.debug(f"CLOSE SHORT UseCase")
        self.broker_api.cancel_all_active_orders(trading_config=trade_intent.trading_config)
        has_short = self.broker_api.have_short_position(trade_intent.trading_config)
        self.messenger_api.send_message(f"#Проверяем наличие открытых шортов: {str(has_short)}")
        if has_short:
            logging.debug(f"Нашли открытый шорт, закрываем")
            self.messenger_api.send_message("#Закрываем SHORT")
            resp = self.broker_api.close_short_position(trade_intent.trading_config)
            self.messenger_api.send_message("#Закрыли SHORT ✅\n" + resp)