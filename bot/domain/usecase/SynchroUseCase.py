import logging

from bot.domain.BrokerApi import BrokerApi
from bot.domain.MessengerApi import MessengerApi
from bot.domain.dto.TradeIntent import SynchroIntent, ShortIntent, LongIntent
from bot.domain.usecase.OpenLongUseCase import OpenLongUseCase
from bot.domain.usecase.OpenShortUseCase import OpenShortUseCase


class SynchroUseCase:
    __broker_api: BrokerApi
    __messenger_api: MessengerApi
    __open_long_usecase: OpenLongUseCase
    __open_short_usecase: OpenShortUseCase

    def __init__(
            self,
            broker_api,
            messenger_api,
            open_long_usecase: OpenLongUseCase,
            open_short_usecase: OpenShortUseCase
    ):
        self.__broker_api = broker_api
        self.__messenger_api = messenger_api
        self.__open_long_usecase = open_long_usecase
        self.__open_short_usecase = open_short_usecase

    def run(self, synchro_intent: SynchroIntent):
        self.__bot_synchronize(synchro_intent)

    def __bot_synchronize(self, synchro_intent: SynchroIntent):
        logging.debug(f"SynchroUseCase: {synchro_intent}")
        have_long = self.__broker_api.have_long_position(synchro_intent.trading_config)
        have_short = self.__broker_api.have_short_position(synchro_intent.trading_config)
        if not have_short and synchro_intent.side == "Sell":
            self.__messenger_api.send_message("#⚠️Расхождение с синхронизирующим сигналом: переходим в Short⚠️")
            self.__open_short_usecase.run(ShortIntent(trading_config= synchro_intent.trading_config, side=synchro_intent.side))

        elif not have_long and synchro_intent.side == "Buy":
            self.__messenger_api.send_message("#⚠️Расхождение с синхронизирующим сигналом: переходим в Long⚠️")
            self.__open_long_usecase.run(LongIntent(trading_config= synchro_intent.trading_config, side=synchro_intent.side))


