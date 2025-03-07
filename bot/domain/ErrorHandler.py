import abc
from abc import ABC

from bot.domain.MessengerApi import MessengerApi


class ErrorHandler(ABC):
    messenger: MessengerApi

    def __init__(self, messenger):
        self.messenger = messenger

    @abc.abstractmethod
    def handle(self, func):
        pass
