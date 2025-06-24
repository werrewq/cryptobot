import abc

from tinkoff.invest import PostOrderResponse, InstrumentType, InstrumentShort, PositionsResponse, \
    Quotation, GetStopOrdersResponse, StopOrderDirection, GetMaxLotsResponse

from tinkoff.invest import OrderDirection


class TinkoffApi:

    @abc.abstractmethod
    def post_market_order(self, figi: str, quantity: int, direction: OrderDirection, account_id: str) -> PostOrderResponse:
        pass

    @abc.abstractmethod
    def cancel_all_orders(self):
        pass

    @abc.abstractmethod
    def cancel_stop_order(self, account_id: str, stop_order_id: str):
        pass

    @abc.abstractmethod
    def find_instruments_by_ticker(self, ticker, instrument_type: InstrumentType) -> list[InstrumentShort]:
        pass

    @abc.abstractmethod
    def get_positions(self, account_id: str) -> PositionsResponse:
        pass

    @abc.abstractmethod
    def get_last_price(self, figi) -> Quotation:
        pass

    @abc.abstractmethod
    def get_stop_orders(self, account_id: str) -> GetStopOrdersResponse:
        pass

    @abc.abstractmethod
    def post_stop_loss_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        pass

    @abc.abstractmethod
    def post_take_profit_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        pass

    @abc.abstractmethod
    def get_max_market_lots(self, account_id: str, figi: str) -> GetMaxLotsResponse:
        pass




