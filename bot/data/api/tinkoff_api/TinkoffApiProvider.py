from bot.config.SecuredConfig import SecuredConfig
from bot.data.api.tinkoff_api.TinkoffApi import TinkoffApi
from bot.data.api.tinkoff_api.TinkoffRealApi import TinkoffRealApi
from bot.data.api.tinkoff_api.TinkoffSandboxApi import TinkoffSandboxApi
from bot.domain.dto.TradingConfig import TradingConfig


class TinkoffApiProvider:
    __trading_config: TradingConfig
    __secured_config: SecuredConfig

    def __init__(self, trading_config: TradingConfig, secured_config: SecuredConfig):
        self.__trading_config = trading_config
        self.__secured_config = secured_config

    def provide(self) -> TinkoffApi:
        if self.__trading_config.sandbox:
            return TinkoffSandboxApi(self.__secured_config)
        else:
            return TinkoffRealApi(self.__secured_config)
