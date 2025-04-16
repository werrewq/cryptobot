import logging
import threading
import traceback
from http.cookiejar import debug

import telebot
from telebot import types

from bot.config.SecuredConfig import SecuredConfig
from bot.domain.MessengerApi import MessengerApi
from bot.presentation.messenger.MessagePresenter import MessagePresenter


class TelegramApi(MessengerApi):

    bot: telebot.TeleBot
    __message_presenter: MessagePresenter

    def __init__(self, secured_config: SecuredConfig, message_presenter:MessagePresenter):
        self.bot = telebot.TeleBot(secured_config.get_telegram_bot_api_token())
        self.setup_handlers()
        self.__message_presenter = message_presenter
        message_presenter.attach_to_view(self)


    def run(self):
        threading.Thread(target=self.start_polling).start()

    def start_polling(self):
        try:
            self.bot.polling(non_stop=True)
        except Exception as e:
            logging.error(
                msg="Ошибка на телеге бота: \n"
                    + repr(e)
                    + "\n"
                    + str(traceback.format_exc())
            )
            self.start_polling()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            print("Telebot start message")
            self.__message_presenter.handle_send_welcome(message.chat.id)

        # Обработчик текстовых сообщений
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            logging.debug("Telebot handle message " + message.text)
            self.__message_presenter.handle_message(message.text, message.chat.id)

    def send_message_to_id(self, message: str, chat_id: int):
        self.bot.send_message(chat_id = chat_id, text=message)

    def show_trade_buttons(self, chat_id):
        markup = self.create_trade_buttons()
        self.bot.send_message(self.__message_presenter.get_authenticated_user_id(), "Добро пожаловать!", reply_markup=markup)

    def create_trade_buttons(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("Торговать")
        button_stop = types.KeyboardButton("Остановка")
        markup.add(button_start)
        markup.add(button_stop)
        return markup

    def send_message(self, message: str):
        chat_id = self.__message_presenter.get_authenticated_user_id()
        logging.debug(f"send_message to chat {str(chat_id)}")
        if chat_id is not None:
            self.bot.send_message(chat_id = self.__message_presenter.get_authenticated_user_id(), text=message)
        else:
            logging.debug(f"send_message chat not yet attached")