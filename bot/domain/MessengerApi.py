import abc

class MessengerApi:

    @abc.abstractmethod
    def send_message(self, message: str): pass

    @abc.abstractmethod
    def send_message_to_id(self, message: str, chat_id: int): pass

    @abc.abstractmethod
    def run(self): pass

    @abc.abstractmethod
    def show_trade_buttons(self, chat_id): pass
