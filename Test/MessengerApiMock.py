from bot.domain.MessengerApi import MessengerApi, TradingStatus


class MessengerApiMock(MessengerApi):

    def send_message(self, message: str):
        print("MessengerApiMock: " + message)

    def get_bot_trading_status(self) -> TradingStatus:
        pass

    def run(self):
        pass