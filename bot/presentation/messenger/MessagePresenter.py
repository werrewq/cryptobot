import logging
from typing import Optional

from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradingStatusInteractor import TradingStatusInteractor, TradingStatus
from bot.presentation.messenger.AuthManager import AuthManager


class MessagePresenter:
    __trading_status_interactor: TradingStatusInteractor
    __messenger_view: MessengerApi
    __auth_manager: AuthManager

    def __init__(self, trading_status_interactor: TradingStatusInteractor, auth_manager: AuthManager):
        self.__trading_status_interactor = trading_status_interactor
        self.__auth_manager = auth_manager

    def attach_to_view(self, messenger_api: MessengerApi):
        self.__messenger_view = messenger_api

    def handle_send_welcome(self, chat_id: int):
        if self.__auth_manager.is_authenticated(chat_id):
            self.__messenger_view.send_message_to_id("Поздравляем! Вы уже авторизированы, начните торговлю.", chat_id)
            self.__messenger_view.show_trade_buttons(chat_id)
        else:
            self.__messenger_view.send_message_to_id("Введите пароль:", chat_id)

    def handle_message(self, message: str, chat_id: int):
        if self.__auth_manager.is_authenticated(chat_id):
            self.__handle_simple_message(message, chat_id)
        else:
            if not self.__auth_manager.was_logged():
                self.process_auf(chat_id, message)
            else:
                self.__messenger_view.send_message_to_id("Бот уже используется другим пользователем", chat_id)

    def process_auf(self, chat_id, message):
        if self.__auth_manager.check_pass(message, chat_id):
            self.__messenger_view.send_message_to_id("Вы успешно авторизировались! Бот готов к работе.", chat_id)
            self.__messenger_view.show_trade_buttons(chat_id)
        else:
            self.__messenger_view.send_message_to_id("Пароль не верный!", chat_id)

    def __handle_simple_message(self, message, chat_id):
        logging.debug("Telebot handle message " + message)
        if message == "Торговать":
            self.__messenger_view.send_message_to_id("Вы нажали на кнопку! Бот начинает торговать.", chat_id)
            self.__trading_status_interactor.set_trading_status(TradingStatus.ONLINE)
        elif message == "Остановка":
            self.__messenger_view.send_message_to_id("Вы нажали на кнопку! Бот засыпает.", chat_id)
            self.__trading_status_interactor.set_trading_status(TradingStatus.OFFLINE)

    def get_authenticated_user_id(self) -> Optional[int]:
        return self.__auth_manager.get_authenticated_user_id()
