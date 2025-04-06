from enum import Enum

class TradingStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TradingStatusInteractor:
    __trading_status: TradingStatus

    def __init__(self):
        self.__trading_status = TradingStatus.OFFLINE

    def get_trading_status(self) -> TradingStatus:
        return self.__trading_status

    def set_trading_status(self, trading_status: TradingStatus):
        self.__trading_status = trading_status

