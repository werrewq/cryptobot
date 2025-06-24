import json
import logging
from typing import Dict, Any

from flask import Flask, request, send_file

from bot.config.SecuredConfig import SecuredConfig
from bot.domain.MessengerApi import MessengerApi
from bot.presentation.logger.BotLogger import BotLogger
from bot.presentation.logger.TradingLogger import TradingLogger
from bot.presentation.worker.RequestTimePriorityQueue import RequestTimePriorityQueue


class SignalController:
    __messenger: MessengerApi
    __flask: Flask = Flask(__name__)
    __logger: BotLogger
    __trade_logger: TradingLogger
    __secured_config: SecuredConfig
    __request_queue: RequestTimePriorityQueue

    def __init__(
            self,
            messenger: MessengerApi,
            logger: BotLogger,
            trade_logger: TradingLogger,
            secured_config: SecuredConfig,
            request_queue: RequestTimePriorityQueue
    ):
        self.__messenger = messenger
        self.__logger = logger
        self.__trade_logger = trade_logger
        self.__secured_config = secured_config
        self.__request_queue = request_queue
        self.setup_handlers()

    def run(self):
        print("Запускаем Flask")
        # self.__flask.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False) # TODO убрать
        return self.__flask

    def setup_handlers(self):

        @self.__flask.route('/position', methods=['GET', 'POST'])
        async def trading_signals():
            json_data = self.get_dict_from_request(request.json)
            if not self.check_token(json_data):
                logging.debug("WRONG TOKEN")
                return "401 Unauthorized"
            logging.debug("Signal from TRADING VIEW \n" + str(json_data["signal"]))
            # Отправляем запрос в очередь задач на выполнение
            self.__request_queue.add_request(json_data)
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
            if message_token == self.__secured_config.get_cryptobot_api_token():
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


