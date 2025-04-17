import logging
from datetime import datetime
from decimal import Decimal

from tinkoff.invest import Client, MoneyValue, OrderType, PostOrderResponse, OrderDirection, InstrumentType, \
    InstrumentShort, PositionsResponse, Quotation, StopOrderStatusOption, GetStopOrdersResponse, StopOrderDirection, \
    StopOrderExpirationType, StopOrderType, PriceType
from tinkoff.invest.constants import INVEST_GRPC_API_SANDBOX
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import decimal_to_quotation

from bot.config.TinkoffSecuredConfig import TinkoffSecuredConfig
from bot.data.api.tinkoff_api.TinkoffApi import TinkoffApi

TOKEN = 'token'

class TinkoffSandboxApi(TinkoffApi):
    __token: str
    __target = INVEST_GRPC_API_SANDBOX
    __account_id: str

    def __init__(self, secured_config: TinkoffSecuredConfig):
        self.__token = secured_config.get_broker_api_key()
        self.__account_id = secured_config.get_broker_account_id()

    def add_money_sandbox(self, account_id, money, currency="rub"):
        with Client(sandbox_token= self.__token, token= self.__token, target=self.__target) as client:
            """Function to add money to sandbox account."""
            money = decimal_to_quotation(Decimal(money))
            resp = client.sandbox.sandbox_pay_in(
                account_id=account_id,
                amount=MoneyValue(units=money.units, nano=money.nano, currency=currency),
            )
            return resp

    def create_sandbox_account(self):
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            sandbox_accounts = client.users.get_accounts()
            # close all sandbox accounts
            for sandbox_account in sandbox_accounts.accounts:
                client.sandbox.close_sandbox_account(account_id=sandbox_account.id)
            # open new sandbox account
            sandbox_account = client.sandbox.open_sandbox_account()
            account_id = sandbox_account.account_id
            logging.debug(f"sandbox account id={str(account_id)}")

    def post_market_order(self, figi: str, quantity: int, direction: OrderDirection, account_id: str) -> PostOrderResponse:
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            r = client.sandbox.post_sandbox_order(
                figi=figi,
                quantity=quantity,
                # price=Quotation(units=1, nano=0),
                account_id=account_id,
                # order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
                #  direction=OrderDirection.ORDER_DIRECTION_SELL,
                direction=direction,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            return r

    def cancel_all_orders(self):
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            orders_response = client.orders.get_orders(account_id=self.__account_id)
            orders = orders_response.orders
            for order in orders:
                try:
                    client.orders.cancel_order(account_id=self.__account_id, order_id=order.id)
                    logging.debug(f"Отменена заявка {order.id} по инструменту {order.figi}")
                except Exception as e:
                    logging.debug(f"Ошибка при отмене заявки {order.id}: {e}")

    def get_stop_orders(self, account_id: str) -> GetStopOrdersResponse:
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            resp = client.stop_orders.get_stop_orders(account_id=account_id, status=StopOrderStatusOption.STOP_ORDER_STATUS_ACTIVE)
            return resp

    def cancel_stop_order(self, account_id: str, stop_order_id: str):
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            client.stop_orders.cancel_stop_order(
                account_id= account_id,
                stop_order_id=stop_order_id
            )

    def post_stop_loss_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            client.stop_orders.post_stop_order(
                account_id=account_id,
                figi=figi,
                quantity=quantity,
                direction=direction,
                stop_price=stop_price,
                expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                stop_order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS,
                price_type=PriceType.PRICE_TYPE_CURRENCY,
                # order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
            )

    def post_take_profit_order(self, figi: str, quantity: int, direction: StopOrderDirection, account_id: str, stop_price: Quotation):
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            client.stop_orders.post_stop_order(
                account_id=account_id,
                figi=figi,
                quantity=quantity,
                direction=direction,
                stop_price=stop_price,
                expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                stop_order_type=StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
                price_type=PriceType.PRICE_TYPE_CURRENCY,
                # order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
            )

    def find_instruments_by_ticker(self, ticker, instrument_type: InstrumentType) -> list[InstrumentShort]:
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            instruments: InstrumentsService = client.instruments
            res = instruments.find_instrument(
                query=ticker,
                instrument_kind=instrument_type,
                api_trade_available_flag=False,
            )
            return res.instruments

    def get_positions(self, account_id: str) -> PositionsResponse:
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            positions = client.operations.get_positions(account_id=account_id)
            return positions

    def get_last_price(self, figi: str) -> Quotation:
        with Client(sandbox_token=self.__token, token=self.__token, target=self.__target) as client:
            # client.orders.get_max_lots
            res = client.market_data.get_last_prices(
                figi= [figi]
            )
            return res.last_prices[0].price