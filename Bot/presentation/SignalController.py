import logging

from flask import Flask, request, jsonify

from Bot.domain.MessengerApi import MessengerApi
from Bot.domain.TradeInteractor import TradeInteractor
from Bot.presentation.SignalToIntentMapper import SignalToIntentMapper

# app = Flask(__name__)

class SignalController:
    __mapper: SignalToIntentMapper
    __messenger: MessengerApi
    __flask: Flask = Flask(__name__)
    __interactor: TradeInteractor

    def __init__(
            self,
            mapper: SignalToIntentMapper,
            messenger: MessengerApi,
            interactor: TradeInteractor,
    ):
        self.__mapper = mapper
        self.__messenger = messenger
        self.__interactor = interactor
        self.setup_handlers()

        # # Настройка логирования
        logging.basicConfig(
            level=logging.DEBUG,  # Уровень логирования
            format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
        )

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
            logging.debug("СИГНАЛ ОТ TRADING VIEW \n" + str(json_data))
            try:
                self.__messenger.send_message("Signal: " + str(json_data))
                intent = self.__mapper.map(json_data)
                await self.__interactor.start_trade(intent)
                return jsonify({"status": "success"})
            except Exception as e:
                print(repr(e))
                self.__messenger.send_message(message="Ошибка обработки сигнала: " + repr(e))
                return jsonify({"status": "internal error"})


