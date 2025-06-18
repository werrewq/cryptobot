import logging
import traceback

from tinkoff.invest import RequestError

from bot.domain.MessengerApi import MessengerApi


class RetryRequestHandler:
    __request_limit: int
    __messenger: MessengerApi

    def __init__(self, request_limit: int, messenger: MessengerApi):
        self.__request_limit = request_limit
        self.__messenger = messenger

    def handle(self, func):
        if self.__request_limit < 1:
            self.__messenger.send_message("RetryRequestHandler: Попытки повторных запросов закончились")
            return "Ошибка запроса"
        try:
            self.__request_limit = self.__request_limit - 1
            return func()
        except RequestError as e:
            logging.error(
                msg="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.code) + " | " + e.details
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            self.__messenger.send_message(
                message="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.code) + " | " + e.details
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            return self.retry_request(func)
        except Exception as e:
            logging.error(
                msg="Ошибка во время запроса на api: \n"
                        + "ByBit API Request Error" + " | "
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            self.__messenger.send_message(
                message="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | "
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            return self.retry_request(func)

    def retry_request(self, func):
        self.__messenger.send_message("RetryRequestHandler: Пробуем повторно выполнить запрос\nrequest_limit=="+str(self.__request_limit))
        return self.handle(func)

class RetryRequestHandlerFabric:
    __messenger: MessengerApi

    def __init__(self, messenger: MessengerApi):
        self.__messenger = messenger

    def create(self, request_limit: int) -> RetryRequestHandler:
        return RetryRequestHandler(request_limit, self.__messenger)