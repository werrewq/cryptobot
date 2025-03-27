import json
import logging
import os
from dataclasses import dataclass

@dataclass
class RawTradingLog:
    coin_name: str
    side: str
    leverage: str
    coin_price: str
    qty: str
    asset_name: str
    available_assets: str

class TradingLogger:
    __log_file_path = os.path.join(os.path.dirname(__file__), 'trading_log.log')
    __logger: logging.Logger

    def __init__(self):
        logger = logging.Logger(name="Trading")
        logger.setLevel(logging.INFO)

        file_handler = self.__set_logs_file_handler()
        console_handler = self.__set_logs_console_handler()

        self.__set_logs_format(console_handler, file_handler)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        self.__logger = logger

    def __set_logs_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        return console_handler

    def __set_logs_file_handler(self):
        file_handler = logging.FileHandler(self.__log_file_path)
        file_handler.setLevel(logging.INFO)
        return file_handler

    def __set_logs_format(self, console_handler, file_handler):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

    def trade_log(self, raw_trading_log: RawTradingLog):
        data = json.dumps({
            "coin_name": raw_trading_log.coin_name,
            "side": raw_trading_log.side,
            "leverage": raw_trading_log.leverage,
            "coin_price": raw_trading_log.coin_price,
            "qty": raw_trading_log.qty,
            "asset_name": raw_trading_log.asset_name,
            "available_assets": raw_trading_log.available_assets,
        })
        self.__logger.info(msg= data)

    def get_logs_path(self):
        return self.__log_file_path
