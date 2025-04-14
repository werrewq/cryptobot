import logging

from pybit.unified_trading import HTTP

from bot.config.SecuredConfig import SecuredConfig
from bot.data.api.ApiHelpers import floor_qty, floor_price
from bot.data.api.CoinPairInfo import CoinPairInfo
from bot.domain.dto.TradingConfig import TradingConfig

MARKET_CATEGORY = "linear"

class BybitApi:

    __client: HTTP
    __coin_pair_info: CoinPairInfo

    def __init__(
            self,
            trading_config: TradingConfig,
            secured_config: SecuredConfig,
    ):
        print("BybitApi init")
        self.__connect_to_api(trading_config, secured_config)

    def __connect_to_api(self, trading_config: TradingConfig, secured_config: SecuredConfig):
        logging.debug(f"Trying connect to Api with demo={str(trading_config.demo)}, testnet={str(trading_config.testnet)}")
        self.__client = HTTP(
            api_key=secured_config.get_broker_api_key(),
            api_secret=secured_config.get_broker_secret_key(),
            recv_window=60000,
            testnet=trading_config.testnet,
            demo=trading_config.demo,
        )

    def get_instruments_info(self, pair_name):
        r = self.__client.get_instruments_info(
            category=MARKET_CATEGORY,
            symbol=pair_name,
        )
        return r

    def get_tickers(self, pair):
        tickers = self.__client.get_tickers(category=MARKET_CATEGORY, symbol=pair)
        return tickers

    def get_wallet_balance(self, coin_name):
        r = self.__client.get_wallet_balance(accountType="UNIFIED", coin=coin_name)
        return r

    def place_order(
            self,
            coin_name,
            side,
            order_value,
            order_message,
    ):
        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=coin_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            qty=str(order_value),
        )

        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n"+ str(r))
        return "Совершена сделка:\n" + order_message

    # def __place_limit_order(self, name, side, price):
    #     self.__client.get_instruments_info(category="spot", symbol="SOLUSDT")
    #     available = self.get_assets(name)
    #
    #     r = self.__client.place_order(
    #         category=MARKET_CATEGORY,
    #         symbol=name + "USDT", # USDT и Name меняются местами
    #         side=side,
    #         orderType="Market",
    #         time_in_force="GoodTillCancel",
    #         qty=floor_qty(available, self.__coin_pair_info),
    #     )
    #     r = self.__client.place_order(
    #         category=MARKET_CATEGORY,
    #         symbol=name + "USDT", # USDT и Name меняются местами
    #         side=side,
    #         orderType="Limit",
    #         time_in_force="GoodTillCancel",
    #         qty=floor_qty(available, self.__coin_pair_info),
    #         price=floor_price(price * 0.99, self.__coin_pair_info),
    #     )
    #
    #     print(str(r))
    #     return str(r)

    def get_positions(self, trading_config):
        json = self.__client.get_positions(
            category=MARKET_CATEGORY,
            symbol=trading_config.target_coin_name + trading_config.asset_name
        )
        return json

    def close_position(self, pair_name, side):
        market_category = MARKET_CATEGORY # Не работает для SPOT
        r = self.__client.place_order(
            # category="linear",
            category=market_category,
            symbol=pair_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            # qty=0.0000000000000000001
            qty=0.0,
            reduceOnly=True,
            closeOnTrigger=True,
        )
        logging.debug("ПОСЛЕ ОТВЕТА BYBIT \n" + str(r))
        return str(r)

    def cancel_all_active_orders(self, symbol):
        self.__client.cancel_all_orders(
            category=MARKET_CATEGORY,
            symbol=symbol
        )

    def set_leverage(self, trading_config):
        r = self.__client.set_leverage(
            category=MARKET_CATEGORY,
            symbol=trading_config.target_coin_name + trading_config.asset_name,
            buyLeverage=str(trading_config.leverage),
            sellLeverage=str(trading_config.leverage),
        )
        return r

    def set_stop_loss(self, pair_name, side, trigger_direction, trigger_price):
        r = self.__client.place_order(
            category=MARKET_CATEGORY,
            symbol=pair_name,
            side=side,
            orderType="Market",
            time_in_force="GoodTillCancel",
            qty=0.0,
            reduceOnly=True,
            closeOnTrigger=True,
            triggerPrice=floor_price(trigger_price, self.__coin_pair_info),
            triggerDirection=trigger_direction,
        )
        return r

