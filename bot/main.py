import logging

from dependency_injector.wiring import Provide, inject

from bot.di.ApplicationContainer import ApplicationContainer
from bot.domain.MessengerApi import MessengerApi
from bot.presentation.SignalController import SignalController
from bot.presentation.logger.BotLogger import BotLogger


class CryptoBot:
    __signal_controller: SignalController
    __messenger_api: MessengerApi

    @inject
    def __init__(
            self,
            signal_controller: SignalController = Provide[ApplicationContainer.signal_controller],
            messenger_api: MessengerApi = Provide[ApplicationContainer.messenger_api],
    ):
        self.__signal_controller = signal_controller
        self.__messenger_api = messenger_api
        pass

    def run(self):
        self.__messenger_api.run()
        flask_app = self.__signal_controller.run()
        return flask_app

def start_bot_locally():
    BotLogger().run()
    # logging.debug("environ \n" + str(environ))
    # logging.debug("start_response \n" + str(start_response))
    container = ApplicationContainer()
    container.wire(modules=[__name__])
    flask_app = CryptoBot().run()
    return flask_app

def start_bot():
    container = ApplicationContainer()
    container.logger.run()
    container.wire(modules=[__name__])
    flask_app = CryptoBot().run()
    return flask_app

# # Точка входа в приложение
if __name__ == '__main__':
    print("MAIN RUN")
    start_bot_locally()



