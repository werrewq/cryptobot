import logging
from enum import Enum

from bot.domain.TradingStatusInteractor import TradingStatusInteractor, TradingStatus


class Authenticated(Enum):
    TRUE = True
    FALSE = False

class MessageHandler:
    __trading_status_interactor: TradingStatusInteractor

    def __init__(self, trading_status_interactor: TradingStatusInteractor):
        self.__trading_status_interactor = trading_status_interactor

    def handle_message(self, message: str, send_message):
        logging.debug("Telebot handle message " + message)
        if message == "Торговать":
            send_message("Вы нажали на кнопку! Бот начинает торговать.")
            self.__trading_status_interactor.set_trading_status(TradingStatus.ONLINE)
        elif message == "Остановка":
            send_message("Вы нажали на кнопку! Бот засыпает.")
            self.__trading_status_interactor.set_trading_status(TradingStatus.OFFLINE)
