import logging

from flask import Flask, request, jsonify

from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradeInteractor import TradeInteractor
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper

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
        self.__flask.run(host='0.0.0.0', port=5001)
        #self.__flask.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)

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


