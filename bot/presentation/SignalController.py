import json
import logging
from typing import Dict, Any

from flask import Flask, request, jsonify, send_file

from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradeInteractor import TradeInteractor
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper
from bot.presentation.logger.BotLogger import BotLogger
from bot.presentation.logger.TradingLogger import TradingLogger

TOKEN = "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"

class SignalController:
    __mapper: SignalToIntentMapper
    __messenger: MessengerApi
    __flask: Flask = Flask(__name__)
    __interactor: TradeInteractor
    __error_handler: ErrorHandler
    __logger: BotLogger
    __trade_logger: TradingLogger

    def __init__(
            self,
            mapper: SignalToIntentMapper,
            messenger: MessengerApi,
            interactor: TradeInteractor,
            error_handler: ErrorHandler,
            logger: BotLogger,
            trade_logger: TradingLogger,
    ):
        self.__mapper = mapper
        self.__messenger = messenger
        self.__interactor = interactor
        self.__error_handler = error_handler
        self.setup_handlers()
        self.__logger = logger
        self.__trade_logger = trade_logger

    def run(self):
        print("Запускаем Flask")
        self.__flask.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False) # TODO убрать
        return self.__flask
        # self.__flask.run(host='0.0.0.0', port=5001)


    def setup_handlers(self):
        @self.__flask.route('/position', methods=['GET', 'POST'])
        async def trading_signals():
            json_data = self.get_dict_from_request(request.json)
            if not self.check_token(json_data):
                logging.debug("WRONG TOKEN")
                return "401 Unauthorized"
            logging.debug("Signal from TRADING VIEW \n" + str(json_data["signal"]))
            self.__messenger.send_message("Signal from TRADING VIEW \n" + str(json_data["signal"]))
            self.__error_handler.handle(lambda : process_signal(json_data))
            return "200"

        @self.__flask.route("/")
        async def base_signal():
            logging.debug("Test Get 200")
            return "200"

        @self.__flask.route('/logs', methods=['GET', 'POST'])
        async def download_logs():
            json_data = self.get_dict_from_request(request.json)
            if not self.check_token(json_data):
                logging.debug("WRONG TOKEN")
                return "401 Unauthorized"
            logging.debug("Logs download request")
            file_path = self.__logger.get_logs_path()
            return send_file(file_path, as_attachment=True)

        @self.__flask.route('/trading_logs', methods=['GET', 'POST'])
        async def download_trade_logs():
            json_data = self.get_dict_from_request(request.json)
            if not self.check_token(json_data):
                logging.debug("WRONG TOKEN")
                return "401 Unauthorized"
            logging.debug("Logs download request")
            file_path = self.__trade_logger.get_logs_path()
            return send_file(file_path, as_attachment=True)

        def process_signal(json_data):
            intent = self.__mapper.map(json_data)
            self.__interactor.start_trade(intent)

    def get_dict_from_request(self, json_data) -> Dict[str, Any]:
        # Проверяем, является ли json_data строкой
        if isinstance(json_data, bytes):
            json_data = json_data.decode('utf-8')  # Декодируем байты в строку
        elif isinstance(json_data, str):
            json_data = json.loads(json_data)  # Преобразуем строку в словарь
        elif isinstance(json_data, Dict):
            pass
        else:
            raise TypeError("Signal JSON has wrong typing")
        return json_data


    def check_token(self, json_data):
        try:
            logging.debug(str(json_data))
            message_token = str(json_data["token"])
            logging.debug(str(message_token))
            if message_token == TOKEN:
                return True
            else:
                return False
        except Exception as e:
            logging.error(
                msg="Ошибка обработки токена: \n"
                    + repr(e)
                    + "\n"
            )
            self.__messenger.send_message(
                message="Ошибка обработки токена: \n"
                    + repr(e)
                    + "\n"
            )
            return False


