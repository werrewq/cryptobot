import threading
from typing import Optional

import telebot
from telebot import types

from Bot.domain.MessengerApi import MessengerApi, TradingStatus

#t.me/SergeySignalBot
# @SergeySignalBot
TELEGRAM_BOT_API_TOKEN = "7848584263:AAH2EY10kySewTnclRLiQf6T9LPoae_yJnk" # убрать в конфиг

class TelegramApi(MessengerApi):
    __trading_status: TradingStatus
    bot: telebot.TeleBot
    __chat_id: Optional[int]

    def __init__(self):
        self.__trading_status = TradingStatus.ONLINE
        # TODO включить заглушку self.__trading_status = TradingStatus.OFFLINE
        self.bot = telebot.TeleBot(TELEGRAM_BOT_API_TOKEN)
        self.setup_handlers()
        self.__chat_id = None

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
            print("Telebot handle message" + message.text)
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