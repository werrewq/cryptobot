import logging

from flask import Flask, request, jsonify

from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradeInteractor import TradeInteractor
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper

TOKEN = "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"

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
        return self.__flask
        # self.__flask.run(host='0.0.0.0', port=5001)
        #self.__flask.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)

    def setup_handlers(self):
        @self.__flask.route('/position', methods=['GET', 'POST'])
        async def trading_signals():
            json_data = request.json
            logging.debug("Signal from TRADING VIEW \n" + str(request))
            if not self.check_token(json_data):
                logging.debug("WRONG TOKEN")
                return "401 Unauthorized"
            logging.debug("Signal from TRADING VIEW \n" + str(json_data))
            self.__messenger.send_message("Signal: " + str(json_data))
            self.__error_handler.handle(lambda : process_signal(json_data))
            return "200"

        @self.__flask.route("/")
        async def base_signal():
            logging.debug("Test Get 200")
            return "200"

        def process_signal(json_data):
            intent = self.__mapper.map(json_data)
            self.__interactor.start_trade(intent)

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


