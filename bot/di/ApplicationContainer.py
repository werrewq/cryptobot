from dependency_injector import containers, providers

from bot.config.Decrypter import Decrypter
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.BybitApi import BybitApi
from bot.data.api.BybitErrorHandler import BybitErrorHandler
from bot.data.api.BybitInteractor import BybitInteractor
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.domain.BrokerApi import BrokerApi
from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradeInteractor import TradeInteractor
from bot.domain.TradingStatusInteractor import TradingStatusInteractor
from bot.domain.dto.TradingConfig import TradingConfig
from bot.domain.usecase.CloseLongUseCase import CloseLongUseCase
from bot.domain.usecase.CloseShortUseCase import CloseShortUseCase
from bot.domain.usecase.OpenLongUseCase import OpenLongUseCase
from bot.domain.usecase.OpenShortUseCase import OpenShortUseCase
from bot.domain.usecase.SetStopLossUseCase import SetStopLossUseCase
from bot.presentation.SignalController import SignalController
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper
from bot.presentation.logger.BotLogger import BotLogger
from bot.presentation.logger.TradingLogger import TradingLogger
from bot.presentation.messenger.AuthManager import AuthManager
from bot.presentation.messenger.MessagePresenter import MessagePresenter
from bot.presentation.messenger.TelegramApi import TelegramApi


class ApplicationContainer(containers.DeclarativeContainer):

    trading_config: TradingConfig = TradingConfigProvider().provide()

    decrypter: Decrypter = providers.Singleton(
        Decrypter,
        key = b'\xda\xff\x84\xceVQ\nr(\x99?\x8b\x074\x05\x1a\xb0\x99\x95\x14z\x96\xd0\n\xf9dB\xa4\xd5j\xcd\xfd'
    )

    secured_config: SecuredConfig = providers.Singleton(
        SecuredConfig,
        trading_config = trading_config,
        decrypter = decrypter,
    )

    logger = providers.Singleton(
        BotLogger
    )

    trading_logger: TradingLogger = providers.Singleton(
        TradingLogger
    )

    auth_manager: AuthManager = providers.Singleton(
        AuthManager,
        secured_config = secured_config
    )

    trading_status_interactor: TradingStatusInteractor = providers.Singleton(
        TradingStatusInteractor,
    )

    message_presenter: MessagePresenter = providers.Singleton(
        MessagePresenter,
        trading_status_interactor = trading_status_interactor,
        auth_manager = auth_manager
    )

    messenger_api: MessengerApi = providers.Singleton(
        TelegramApi,
        secured_config = secured_config,
        message_presenter = message_presenter,
    )

    retry_request_handler_fabric: RetryRequestHandlerFabric = providers.Singleton(
        RetryRequestHandlerFabric,
        messenger = messenger_api,
    )

    signal_to_intent_mapper = providers.Factory(
        SignalToIntentMapper,
        trading_config = trading_config,
    )

    bybit_api: BybitApi = providers.Singleton(
        BybitApi,
        trading_config=trading_config,
        secured_config=secured_config,
    )

    broker_api: BrokerApi = providers.Singleton(
        BybitInteractor,
        bybit_api = bybit_api,
        retry_request_fabric=retry_request_handler_fabric,
        trading_config = trading_config,
        trading_logger = trading_logger,
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

    set_stop_loss_usecase = providers.Factory(
        SetStopLossUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api
    )

    trade_interactor: TradeInteractor = providers.Factory(
        TradeInteractor,
        open_long_usecase = open_long_usecase,
        open_short_usecase = open_short_usecase,
        set_stop_loss_usecase = set_stop_loss_usecase,
        messenger_api = messenger_api,
        trading_status_interactor = trading_status_interactor
    )

    error_handler: ErrorHandler = providers.Singleton(
        BybitErrorHandler,
        messenger = messenger_api,
    )

    signal_controller: SignalController = providers.Singleton(
        SignalController,
        mapper = signal_to_intent_mapper,
        messenger = messenger_api,
        interactor = trade_interactor,
        error_handler = error_handler,
        logger = logger,
        trade_logger = trading_logger,
        secured_config = secured_config
    )
