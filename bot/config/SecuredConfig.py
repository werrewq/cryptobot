import abc
import os

from bot.config.Decrypter import Decrypter
from bot.domain.dto.TradingConfig import TradingConfig

test_chat_pass = "qwerty"

# ENCRYPTED TEST DATA:
test_broker_api_key=""
broker_account_id=""
test_telegram_bot_api_token=""
test_cryptobot_api_token=""

class EnvironmentVariables:

    @abc.abstractmethod
    def get_broker_api_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_broker_account_id(self) -> str:
        pass

    @abc.abstractmethod
    def get_telegram_bot_api_token(self) -> str:
        pass

    @abc.abstractmethod
    def get_cryptobot_api_token(self) -> str:
        pass

    @abc.abstractmethod
    def get_chat_pass(self) -> str:
        pass

class TestEnvironmentVariables(EnvironmentVariables):

    def get_broker_account_id(self) -> str:
        return broker_account_id

    def get_chat_pass(self) -> str:
        return test_chat_pass

    def get_broker_api_key(self) -> str:
        return test_broker_api_key

    def get_telegram_bot_api_token(self) -> str:
        return test_telegram_bot_api_token

    def get_cryptobot_api_token(self) -> str:
        return test_cryptobot_api_token

class OsEnvironmentVariables(EnvironmentVariables):

    def get_broker_account_id(self) -> str:
        return os.environ["BROKER_ACCOUNT_ID"]

    def get_chat_pass(self) -> str:
        return os.environ["CHAT_PASS"]

    def get_broker_api_key(self) -> str:
        return os.environ["BROKER_API_KEY"]

    def get_telegram_bot_api_token(self) -> str:
        return os.environ["TELEGRAM_BOT_API_TOKEN"]

    def get_cryptobot_api_token(self) -> str:
        return os.environ["CRYPTOBOT_API_TOKEN"]

class SecuredConfig(EnvironmentVariables):
    __environment_variables: EnvironmentVariables
    __decrypter: Decrypter

    def __init__(self, trading_config: TradingConfig, decrypter: Decrypter):
        if trading_config.test_env_vars:
            self.__environment_variables = TestEnvironmentVariables()
        else:
            self.__environment_variables = OsEnvironmentVariables()
        self.__decrypter = decrypter

    def get_broker_api_key(self) -> str:
        key = self.__environment_variables.get_broker_api_key()
        return self.__decrypter.decrypt(key)

    def get_telegram_bot_api_token(self) -> str:
        key = self.__environment_variables.get_telegram_bot_api_token()
        return self.__decrypter.decrypt(key)

    def get_cryptobot_api_token(self) -> str:
        key = self.__environment_variables.get_cryptobot_api_token()
        return self.__decrypter.decrypt(key)

    def get_chat_pass(self):
        return self.__environment_variables.get_chat_pass()

    def get_broker_account_id(self):
        id = self.__environment_variables.get_broker_account_id()
        return self.__decrypter.decrypt(id)
