import abc

class MessengerApi:

    @abc.abstractmethod
    def send_message(self, message: str): pass

    @abc.abstractmethod
    def run(self): pass