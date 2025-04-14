from bot.domain.MessengerApi import MessengerApi


class MessengerApiMock(MessengerApi):

    def send_message(self, message: str):
        print("MessengerApiMock: " + message)

    def run(self):
        pass