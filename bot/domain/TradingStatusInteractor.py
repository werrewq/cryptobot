import logging
from enum import Enum

class TradingStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TradingStatusInteractor:
    __trading_status: TradingStatus

    def __init__(self):
        # self.__trading_status = TradingStatus.OFFLINE
        self.__trading_status = TradingStatus.ONLINE # TODO когда бот падает, надо чтобы он продолжил торговать при рестарте

    def get_trading_status(self) -> TradingStatus:
        status = self.__trading_status
        logging.debug("get_trading_status == " + str(status.value))
        return status

    def set_trading_status(self, trading_status: TradingStatus):
        logging.debug("set_trading_status == " + str(trading_status.value))
        self.__trading_status = trading_status

