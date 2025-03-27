import abc
import os

from bot.domain.dto.TradingConfig import TradingConfig

# Тестовые ключи
# test_broker_api_key = "6pAf7l2HZn46GqJqu6"
# test_broker_secret_key = "FHfaEudS6euKkiVobB6cDTkDzXs6TIBhX9Iu"
test_broker_api_key = "ZcNKoTlZYkouIPeXGE"
test_broker_secret_key = "3EEwQjfzXwyOh72bHjQEB7prHQEBODIk044E"
test_telegram_bot_api_token = "7848584263:AAH2EY10kySewTnclRLiQf6T9LPoae_yJnk"
test_cryptobot_api_token = "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
# $env:BROKER_API_KEY = "ZcNKoTlZYkouIPeXGE"
# $env:BROKER_SECRET_KEY = "3EEwQjfzXwyOh72bHjQEB7prHQEBODIk044E"
# $env:TELEGRAM_BOT_API_TOKEN = "7848584263:AAH2EY10kySewTnclRLiQf6T9LPoae_yJnk"
# $env:CRYPTOBOT_API_TOKEN = "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"

# only server
# test_broker_api_key ZcNKoTlZYkouIPeXGE
# test_broker_secret_key 3EEwQjfzXwyOh72bHjQEB7prHQEBODIk044E

class EnvironmentVariables:

    @abc.abstractmethod
    def get_broker_api_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_broker_secret_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_telegram_bot_api_token(self) -> str:
        pass

    @abc.abstractmethod
    def get_cryptobot_api_token(self) -> str:
        pass

class TestEnvironmentVariables(EnvironmentVariables):
    def get_broker_api_key(self) -> str:
        return test_broker_api_key

    def get_broker_secret_key(self) -> str:
        return test_broker_secret_key

    def get_telegram_bot_api_token(self) -> str:
        return test_telegram_bot_api_token

    def get_cryptobot_api_token(self) -> str:
        return test_cryptobot_api_token

class OsEnvironmentVariables(EnvironmentVariables):
    def get_broker_api_key(self) -> str:
        return os.environ["BROKER_API_KEY"]

    def get_broker_secret_key(self) -> str:
        return os.environ["BROKER_SECRET_KEY"]

    def get_telegram_bot_api_token(self) -> str:
        return os.environ["TELEGRAM_BOT_API_TOKEN"]

    def get_cryptobot_api_token(self) -> str:
        return os.environ["CRYPTOBOT_API_TOKEN"]

class SecuredConfig(EnvironmentVariables):
    __environment_variables: EnvironmentVariables

    def __init__(self, trading_config: TradingConfig):
        if trading_config.test_env_vars:
            self.__environment_variables = TestEnvironmentVariables()
        else:
            self.__environment_variables = OsEnvironmentVariables()

    def get_broker_api_key(self) -> str:
        return self.__environment_variables.get_broker_api_key()

    def get_broker_secret_key(self) -> str:
        return self.__environment_variables.get_broker_secret_key()

    def get_telegram_bot_api_token(self) -> str:
        return self.__environment_variables.get_telegram_bot_api_token()

    def get_cryptobot_api_token(self) -> str:
        return self.__environment_variables.get_cryptobot_api_token()