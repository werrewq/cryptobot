import logging
import traceback

from pybit import exceptions

from bot.domain.ErrorHandler import ErrorHandler


class BybitErrorHandler(ErrorHandler):

    def __init__(self, messenger):
        super().__init__(messenger)

    def handle(self, func):
        try:
            func()
        except exceptions.InvalidRequestError as e:
            logging.error(
                msg="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.status_code) + " | " + e.message
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            self.messenger.send_message(
                message="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.status_code) + " | " + e.message
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
        except exceptions.FailedRequestError as e:
            logging.error(
                msg="Ошибка во время запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.status_code) + " | " + e.message
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
            self.messenger.send_message(
                message="Ошибка неправильного запроса на api: \n"
                        + "ByBit API Request Error" + " | " + str(e.status_code) + " | " + e.message
                        + repr(e)
                        + "\n"
                        + str(traceback.format_exc())
            )
        except Exception as e:
            logging.error(
                msg="Ошибка на боте: \n"
                    + repr(e)
                    + "\n"
                    + str(traceback.format_exc())
            )
            self.messenger.send_message(
                message="Ошибка на боте: \n"
                    + repr(e)
                    + "\n"
                    + str(traceback.format_exc())
            )
