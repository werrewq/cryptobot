from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import RevertLimitIntent


class SetRevertLimitUseCase:
    broker_api: BrokerApi
    messenger_api: MessengerApi

    def __init__(self, broker_api, messenger_api):
        self.broker_api = broker_api
        self.messenger_api = messenger_api

    def run(self, revert_limit_intent: RevertLimitIntent):
        self.__bot_set_revert_limit(revert_limit_intent)

    def __bot_set_revert_limit(self, revert_limit_intent: RevertLimitIntent):
        self.messenger_api.send_message(message="Пробуем закрыть все старые ордера")
        self.broker_api.cancel_all_active_orders(revert_limit_intent.trading_config)
        self.messenger_api.send_message(message=f"Пробуем поставить REVERT LIMIT ↩️: {revert_limit_intent.side} на высоте {revert_limit_intent.trigger_price}")
        message = self.broker_api.set_revert_limit(revert_limit_intent)
        self.messenger_api.send_message(message=message)