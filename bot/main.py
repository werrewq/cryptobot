from dependency_injector.wiring import Provide, inject

from bot.di.ApplicationContainer import ApplicationContainer
from bot.domain.MessengerApi import MessengerApi
from bot.presentation.SignalController import SignalController
from bot.presentation.worker.RequestEventLoop import RequestEventLoop


class CryptoBot:
    __signal_controller: SignalController
    __messenger_api: MessengerApi
    __request_event_loop: RequestEventLoop

    @inject
    def __init__(
            self,
            request_event_loop: RequestEventLoop = Provide[ApplicationContainer.request_event_loop],
            signal_controller: SignalController = Provide[ApplicationContainer.signal_controller],
            messenger_api: MessengerApi = Provide[ApplicationContainer.messenger_api],
    ):
        self.__request_event_loop = request_event_loop
        self.__signal_controller = signal_controller
        self.__messenger_api = messenger_api
        pass

    def run(self):
        self.__messenger_api.run()
        self.__request_event_loop.start()
        flask_app = self.__signal_controller.run()
        return flask_app

def start_bot_locally():
    container = ApplicationContainer()
    container.wire(modules=[__name__])
    container.logger().run()
    container.tinkoff_logger().run()
    flask_app = CryptoBot().run()
    flask_app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)

def start_bot():
    container = ApplicationContainer()
    container.wire(modules=[__name__])
    container.logger().run()
    container.tinkoff_logger().run()
    flask_app = CryptoBot().run()
    return flask_app

# Точка входа в приложение
# if __name__ == '__main__':
#     print("MAIN RUN")
#     start_bot_locally()



