import logging

from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradingStatusInteractor import TradingStatusInteractor, TradingStatus
from bot.domain.dto.TradeIntent import LongIntent, ShortIntent, TradeIntent, StopLossIntent, TakeProfitIntent
from bot.domain.usecase import OpenLongUseCase, OpenShortUseCase, SetStopLossUseCase, SetTakeProfitUseCase


class TradeInteractor:
    __open_long_usecase: OpenLongUseCase
    __open_short_usecase: OpenShortUseCase
    __messenger: MessengerApi
    __set_stop_loss_usecase: SetStopLossUseCase
    __trading_status_interactor: TradingStatusInteractor
    __set_take_profit_usecase: SetTakeProfitUseCase

    def __init__(
            self,
            open_long_usecase: OpenLongUseCase,
            open_short_usecase: OpenShortUseCase,
            set_stop_loss_usecase: SetStopLossUseCase,
            set_take_profit_usecase: SetTakeProfitUseCase,
            messenger_api: MessengerApi,
            trading_status_interactor: TradingStatusInteractor,
    ):
        self.__open_long_usecase = open_long_usecase
        self.__open_short_usecase = open_short_usecase
        self.__messenger = messenger_api
        self.__set_stop_loss_usecase = set_stop_loss_usecase
        self.__trading_status_interactor = trading_status_interactor
        self.__set_take_profit_usecase = set_take_profit_usecase

    def start_trade(self, trade_intent: TradeIntent):
        self.__messenger.send_message("Пришла заявка на торговлю: " + trade_intent.trading_config.target_share_name)
        trading_status = self.__trading_status_interactor.get_trading_status()
        if trading_status == TradingStatus.OFFLINE:
            logging.debug("set_trading_status == " + str(trading_status.value))
            self.__messenger.send_message("Бот не торгует, статус OFFLINE")
            return

        match trade_intent:
            case LongIntent():
                self.__open_long_usecase.run(trade_intent)

            case ShortIntent():
                self.__open_short_usecase.run(trade_intent)

            case StopLossIntent():
                self.__set_stop_loss_usecase.run(trade_intent)

            case TakeProfitIntent():
                self.__set_take_profit_usecase.run(trade_intent)

            case _:
                raise TypeError('Unsupported type')

