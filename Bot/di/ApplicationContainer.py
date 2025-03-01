from dependency_injector import containers, providers

from Bot.data.api.BybitApi import BybitApi
from Bot.domain.BrokerApi import BrokerApi
from Bot.domain.MessengerApi import MessengerApi
from Bot.domain.TradeInteractor import TradeInteractor
from Bot.domain.usecase.CloseLongUseCase import CloseLongUseCase
from Bot.domain.usecase.CloseShortUseCase import CloseShortUseCase
from Bot.domain.usecase.OpenLongUseCase import OpenLongUseCase
from Bot.domain.usecase.OpenShortUseCase import OpenShortUseCase
from Bot.presentation.SignalController import SignalController
from Bot.presentation.SignalToIntentMapper import SignalToIntentMapper
from Bot.presentation.messenger.TelegramApi import TelegramApi


class ApplicationContainer(containers.DeclarativeContainer):

    # config = providers.Configuration()
    #
    # api_client = providers.Singleton(
    #     ApiClient,
    #     api_key=config.api_key,
    #     timeout=config.timeout,
    # )
    #
    # service = providers.Factory(
    #     Service,
    #     api_client=api_client,
    # )

    messenger_api: MessengerApi = providers.Singleton(
        TelegramApi,
    )

    signal_to_intent_mapper = providers.Factory(
        SignalToIntentMapper
    )

    broker_api: BrokerApi = providers.Singleton(
        BybitApi,
    )

    close_short_usecase = providers.Factory(
        CloseShortUseCase,
        broker_api=broker_api,
        messenger_api=messenger_api,
    )

    close_long_usecase = providers.Factory(
        CloseLongUseCase,
        broker_api=broker_api,
        messenger_api=messenger_api,
    )

    open_long_usecase = providers.Factory(
        OpenLongUseCase,
        broker_api=broker_api,
        messenger_api=messenger_api,
        close_short_usecase=close_short_usecase
    )

    open_short_usecase = providers.Factory(
        OpenShortUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api,
        close_long_usecase = close_long_usecase
    )

    trade_interactor: TradeInteractor = providers.Factory(
        TradeInteractor,
        open_long_usecase = open_long_usecase,
        open_short_usecase = open_short_usecase,
        messenger_api = messenger_api,
    )

    signal_controller: SignalController = providers.Singleton(
        SignalController,
        mapper = signal_to_intent_mapper,
        messenger = messenger_api,
        interactor = trade_interactor,
    )
