import logging
import os

import tinkoff.invest


class TinkoffLogger:
    # D:\dev\bot\CryptoBot\cryptobot\Bot\logs
    # __log_file_path = os.path.join(os.path.dirname(__file__),'..','..', 'logs', 'debug_log.log')
    __log_file_path = os.path.join(os.path.dirname(__file__), 'debug_log.log')

    def run(self):

        logger = tinkoff.invest.logging.logger
        logger.setLevel(logging.DEBUG)

        file_handler = self.set_logs_file_handler()
        console_handler = self.set_logs_console_handler()

        self.set_logs_format(console_handler, file_handler)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Пример использования
        # logger.debug("LOGGING TEST")
        # logger.info("LOGGING TEST")
        # logger.warning("LOGGING TEST")
        # logger.error("LOGGING TEST")
        # logger.critical("LOGGING TEST")

    def set_logs_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        return console_handler

    def set_logs_file_handler(self):
        file_handler = logging.FileHandler(self.__log_file_path)
        file_handler.setLevel(logging.DEBUG)
        return file_handler

    def set_logs_format(self, console_handler, file_handler):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

    def get_logs_path(self):
        return self.__log_file_path
