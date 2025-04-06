import abc
from enum import Enum


class TradingStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class MessengerApi:

    @abc.abstractmethod
    def send_message(self, message: str): pass

    @abc.abstractmethod
    def get_bot_trading_status(self) -> TradingStatus: pass

    @abc.abstractmethod
    def run(self): pass