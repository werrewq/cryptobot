import logging

from tinkoff.invest import Client, OrderType, PostOrderResponse, OrderDirection, InstrumentType, \
    InstrumentShort, PositionsResponse, Quotation, StopOrderStatusOption, GetStopOrdersResponse, StopOrderDirection, \
    StopOrderExpirationType, StopOrderType, PriceType, GetMaxLotsRequest, GetMaxLotsResponse, TakeProfitType, \
    ExchangeOrderType
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.services import InstrumentsService

from bot.config.SecuredConfig import SecuredConfig
from bot.data.api.tinkoff_api.TinkoffApi import TinkoffApi


class TinkoffRealApi(TinkoffApi):
    __token: str
    __target = INVEST_GRPC_API
    __account_id: str

    def __init__(self, secured_config: SecuredConfig):
        self.__token = secured_config.get_broker_api_key()
        self.__account_id = secured_config.get_broker_account_id()

    def client_show_all_accounts(self):
        with Client(token=self.__token, target=self.__target) as client:
            res = client.users.get_accounts()
            print("___ALL ACCOUNTS___")
            for account in res.accounts:
                print(str(account))

    def post_market_order(self, figi: str, quantity: int, direction: OrderDirection, account_id: str) -> PostOrderResponse:
        with Client(token=self.__token, target=self.__target) as client:
            r = client.orders.post_order(
                figi=figi,
                quantity=quantity,
                account_id=account_id,
                direction=direction,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            return r

    def cancel_all_orders(self):
        with Client(token=self.__token, target=self.__target) as client:
            orders_response = client.orders.get_orders(account_id=self.__account_id)
            orders = orders_response.orders
            for order in orders:
                try:
                    client.orders.cancel_order(account_id=self.__account_id, order_id=order.order_id)
                    logging.debug(f"Отменена заявка {order.order_id} по инструменту {order.figi}")
                except Exception as e:
                    logging.debug(f"Ошибка при отмене заявки {order.order_id}: {e}")

    def have_active_orders(self) -> bool:
        with Client(token=self.__token, target=self.__target) as client:
            orders_response = client.orders.get_orders(account_id=self.__account_id)
            orders = orders_response.orders
            return len(orders) != 0

    def get_stop_orders(self, account_id: str) -> GetStopOrdersResponse:
        with Client(token=self.__token, target=self.__target) as client:
            resp = client.stop_orders.get_stop_orders(account_id=account_id, status=StopOrderStatusOption.STOP_ORDER_STATUS_ACTIVE)
            return resp

    def cancel_stop_order(self, account_id: str, stop_order_id: str):
        with Client(token=self.__token, target=self.__target) as client:
            client.stop_orders.cancel_stop_order(
                account_id= account_id,
                stop_order_id=stop_order_id
            )

    def post_stop_loss_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        with Client(token=self.__token, target=self.__target) as client:
            client.stop_orders.post_stop_order(
                account_id=account_id,
                figi=figi,
                quantity=quantity,
                direction=direction,
                stop_price=stop_price,
                expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                stop_order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS,
                price_type=PriceType.PRICE_TYPE_CURRENCY,
            )

    def post_take_profit_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        with Client(token=self.__token, target=self.__target) as client:
            client.stop_orders.post_stop_order(
                account_id=account_id,
                figi=figi,
                quantity=quantity,
                direction=direction,
                stop_price=stop_price,
                expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                stop_order_type=StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
                take_profit_type=TakeProfitType.TAKE_PROFIT_TYPE_REGULAR,
                exchange_order_type=ExchangeOrderType.EXCHANGE_ORDER_TYPE_MARKET,
                price_type=PriceType.PRICE_TYPE_CURRENCY,
            )

    def find_instruments_by_ticker(self, ticker, instrument_type: InstrumentType) -> list[InstrumentShort]:
        with Client(token=self.__token, target=self.__target) as client:
            instruments: InstrumentsService = client.instruments
            res = instruments.find_instrument(
                query=ticker,
                instrument_kind=instrument_type,
                api_trade_available_flag=True,
            )
            return res.instruments

    def get_positions(self, account_id: str) -> PositionsResponse:
        with Client(token=self.__token, target=self.__target) as client:
            positions = client.operations.get_positions(account_id=account_id)
            return positions

    def get_last_price(self, figi: str) -> Quotation:
        with Client( token=self.__token, target=self.__target) as client:
            res = client.market_data.get_last_prices(
                figi= [figi]
            )
            return res.last_prices[0].price

    def get_max_market_lots(self, account_id: str, figi: str) -> GetMaxLotsResponse:
        with Client(token=self.__token, target=self.__target) as client:
            res = client.orders.get_max_lots(
                request=GetMaxLotsRequest(
                    account_id=account_id,
                    instrument_id=figi,
                )
            )
            return res