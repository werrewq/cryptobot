import asyncio
import logging

from flask import Flask, request, jsonify

from Bot.domain.ErrorHandler import ErrorHandler
from Bot.domain.MessengerApi import MessengerApi
from Bot.domain.TradeInteractor import TradeInteractor
from Bot.presentation.SignalToIntentMapper import SignalToIntentMapper

# app = Flask(__name__)

class SignalController:
    __mapper: SignalToIntentMapper
    __messenger: MessengerApi
    __flask: Flask = Flask(__name__)
    __interactor: TradeInteractor
    __error_handler: ErrorHandler

    def __init__(
            self,
            mapper: SignalToIntentMapper,
            messenger: MessengerApi,
            interactor: TradeInteractor,
            error_handler: ErrorHandler
    ):
        self.__mapper = mapper
        self.__messenger = messenger
        self.__interactor = interactor
        self.__error_handler = error_handler
        self.setup_handlers()

    def run(self):
        print("Запускаем Flask")
        self.__flask.run()
        #self.__flask.run(host='0.0.0.0', port=8080, debug=True)

    def setup_handlers(self):
        @self.__flask.route('/position', methods=['GET', 'POST'])
        async def trading_signals():
            print("Входящее оповещение")
            json_data = request.json
            print("Signal: " + str(json_data))
            logging.debug("Signal from TRADING VIEW \n" + str(json_data))
            self.__messenger.send_message("Signal: " + str(json_data))
            self.__error_handler.handle(lambda : process_signal(json_data))
            return jsonify({"status": "success"})

        def process_signal(json_data):
            intent = self.__mapper.map(json_data)
            self.__interactor.start_trade(intent)


