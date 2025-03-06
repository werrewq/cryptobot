from Bot.domain.MessengerApi import MessengerApi, TradingStatus
from Bot.domain.dto.TradeIntent import LongIntent, ShortIntent, TradeIntent
from Bot.domain.usecase import OpenLongUseCase, OpenShortUseCase

class TradeInteractor:
    __open_long_usecase: OpenLongUseCase
    __open_short_usecase: OpenShortUseCase
    __messenger: MessengerApi

    def __init__(
            self,
            open_long_usecase,
            open_short_usecase,
            messenger_api: MessengerApi,
    ):
        self.__open_long_usecase = open_long_usecase
        self.__open_short_usecase = open_short_usecase
        self.__messenger = messenger_api

    def start_trade(self, trade_intent: TradeIntent):
        self.__messenger.send_message("Пришла заявка на торговлю: " + trade_intent.trading_config.target_coin_name)
        trading_status = self.__messenger.get_bot_trading_status()
        if trading_status == TradingStatus.OFFLINE:
            print("TradingStatus.OFFLINE")
            self.__messenger.send_message("Бот не торгует, статус OFFLINE " + trade_intent.trading_config.target_coin_name)
            return

        match trade_intent:
            case LongIntent():
                self.__open_long_usecase.run(trade_intent)

            case ShortIntent():
                self.__open_short_usecase.run(trade_intent)
            case _:
                raise TypeError('Unsupported type')