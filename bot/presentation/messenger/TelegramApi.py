import logging
import threading
from typing import Optional

import telebot
from telebot import types

from bot.config.SecuredConfig import SecuredConfig
from bot.domain.MessengerApi import MessengerApi
from bot.presentation.messenger.MessageHandler import MessageHandler


class TelegramApi(MessengerApi):
    bot: telebot.TeleBot
    __chat_id: Optional[int]
    __message_handler: MessageHandler

    def __init__(self, secured_config: SecuredConfig, message_handler:MessageHandler):
        self.bot = telebot.TeleBot(secured_config.get_telegram_bot_api_token())
        self.setup_handlers()
        self.__chat_id = None
        self.__message_handler = message_handler


    def run(self):
        threading.Thread(target=self.start_polling).start()

    def start_polling(self):
        self.bot.polling(non_stop=True)

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.__chat_id = message.chat.id
            print("Telebot start message")
            markup = create_buttons()
            self.bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)

        # @bot.message_handler(func=lambda message: True)
        # def handle_message(message):
        #     user_id = message.from_user.id
        #
        #     # Проверяем, есть ли пользователь в состоянии ожидания пароля
        #     if user_id not in user_states:
        #         user_states[user_id] = False  # Пользователь еще не ввел пароль
        #
        #     if not user_states[user_id]:
        #         # Если пользователь еще не ввел пароль, проверяем его
        #         if message.text == PASSWORD:
        #             user_states[user_id] = True  # Устанавливаем состояние как "введен пароль"
        #             bot.send_message(message.chat.id, "Пароль верный! Теперь вы можете использовать команду /secret.")
        #         else:
        #             bot.send_message(message.chat.id, "Неверный пароль. Попробуйте снова.")
        #     else:
        #         # Если пароль уже введен, обрабатываем команды
        #         if message.text == "/secret":
        #             bot.send_message(message.chat.id, "Это секретное сообщение!")
        #         else:
        #             bot.send_message(message.chat.id, "Вы можете использовать команду /secret.")

        def create_buttons():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_start = types.KeyboardButton("Торговать")
            button_stop = types.KeyboardButton("Остановка")
            markup.add(button_start)
            markup.add(button_stop)
            return markup

        # Обработчик текстовых сообщений
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            logging.debug("Telebot handle message " + message.text)
            send_message = lambda txt: self.bot.send_message(message.chat.id, txt)
            self.__message_handler.handle_message(message.text, send_message)

            if message.text == "Торговать":
                self.bot.send_message(message.chat.id, "Вы нажали на кнопку! Бот начинает торговать.")
                self.__trading_status = TradingStatus.ONLINE
            elif message.text == "Остановка":
                self.bot.send_message(message.chat.id, "Вы нажали на кнопку! Бот засыпает.")
                self.__trading_status = TradingStatus.OFFLINE

    def send_message(self, message: str):
        if self.__chat_id is not None:
            self.bot.send_message(chat_id = self.__chat_id, text=message)

    def get_bot_trading_status(self) -> TradingStatus:
        return self.__trading_status