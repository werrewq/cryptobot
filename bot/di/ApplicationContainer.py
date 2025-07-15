from dependency_injector import containers, providers

from bot.config.Decrypter import Decrypter
from bot.config.SecuredConfig import SecuredConfig
from bot.config.TradingConfigProvider import TradingConfigProvider
from bot.data.api.BybitErrorHandler import BybitErrorHandler
from bot.data.api.RetryRequestHandler import RetryRequestHandlerFabric
from bot.data.api.tinkoff_api.TinkoffApiProvider import TinkoffApiProvider
from bot.data.api.tinkoff_api.TinkoffInteractor import TinkoffInteractor
from bot.domain.BrokerApi import BrokerApi
from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.SaveTimer import SaveTimer
from bot.domain.TradeInteractor import TradeInteractor
from bot.domain.TradingStatusInteractor import TradingStatusInteractor
from bot.domain.dto.TradingConfig import TradingConfig
from bot.domain.usecase.CloseAllUseCase import CloseAllUseCase
from bot.domain.usecase.CloseLongUseCase import CloseLongUseCase
from bot.domain.usecase.CloseShortUseCase import CloseShortUseCase
from bot.domain.usecase.OpenLongUseCase import OpenLongUseCase
from bot.domain.usecase.OpenShortUseCase import OpenShortUseCase
from bot.domain.usecase.SetStopLossUseCase import SetStopLossUseCase
from bot.domain.usecase.SetTakeProfitUseCase import SetTakeProfitUseCase
from bot.domain.usecase.SetRevertLimitUseCase import SetRevertLimitUseCase
from bot.domain.usecase.SynchroUseCase import SynchroUseCase
from bot.presentation.SignalController import SignalController
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper
from bot.presentation.logger.BotLogger import BotLogger
from bot.presentation.logger.TinkoffLogger import TinkoffLogger
from bot.presentation.logger.TradingLogger import TradingLogger
from bot.presentation.messenger.AuthManager import AuthManager
from bot.presentation.messenger.MessagePresenter import MessagePresenter
from bot.presentation.messenger.TelegramApi import TelegramApi
from bot.presentation.worker.EventLoop import EventLoop
from bot.presentation.worker.RequestEventLoop import RequestEventLoop
from bot.presentation.worker.RequestTimePriorityQueue import RequestTimePriorityQueue


class ApplicationContainer(containers.DeclarativeContainer):

    trading_config: TradingConfig = TradingConfigProvider().provide()

    decrypter: Decrypter = providers.Singleton(
        Decrypter,
        key = b'y\xe8>V\xeb\x1dK\xdb\xaa\x1ac\xea\x88\xae\x93#\x91\x0b\xa6\x13\x08\xfeX85\x9b\xf0\x0b\xd3%\xf8\xcb'
        # local debug key=b'\xda\xff\x84\xceVQ\nr(\x99?\x8b\x074\x05\x1a\xb0\x99\x95\x14z\x96\xd0\n\xf9dB\xa4\xd5j\xcd\xfd'
    )

    secured_config = providers.Singleton(
        SecuredConfig,
        trading_config = trading_config,
        decrypter = decrypter,
    )

    logger = providers.Singleton(
        BotLogger
    )

    tinkoff_logger = providers.Singleton(
        TinkoffLogger
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

    tinkoff_api = TinkoffApiProvider(trading_config= trading_config, secured_config=secured_config()).provide()

    broker_api: BrokerApi = providers.Singleton(
        TinkoffInteractor,
        tinkoff_api = tinkoff_api,
        secured_config= secured_config,
        trading_config = trading_config,
        retry_request_fabric = retry_request_handler_fabric,
    )

    # close_short_usecase = providers.Factory(
    #     CloseShortUseCase,
    #     broker_api=broker_api,
    #     messenger_api=messenger_api,
    # )
    #
    # close_long_usecase = providers.Factory(
    #     CloseLongUseCase,
    #     broker_api=broker_api,
    #     messenger_api=messenger_api,
    # )

    open_long_usecase = providers.Factory(
        OpenLongUseCase,
        broker_api=broker_api,
        messenger_api=messenger_api,
    )

    open_short_usecase = providers.Factory(
        OpenShortUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api,
    )

    set_stop_loss_usecase = providers.Factory(
        SetStopLossUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api
    )

    set_take_profit_usecase = providers.Factory(
        SetTakeProfitUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api
    )

    set_revert_limit_usecase = providers.Factory(
        SetRevertLimitUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api
    )

    close_all_usecase = providers.Factory(
        CloseAllUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api
    )

    synchro_usecase = providers.Factory(
        SynchroUseCase,
        broker_api = broker_api,
        messenger_api = messenger_api,
        open_long_usecase=open_long_usecase,
        open_short_usecase=open_short_usecase,
    )

    save_timer: SaveTimer = providers.Singleton(
        SaveTimer,
        trading_config = trading_config
    )

    trade_interactor: TradeInteractor = providers.Factory(
        TradeInteractor,
        open_long_usecase = open_long_usecase,
        open_short_usecase = open_short_usecase,
        set_stop_loss_usecase = set_stop_loss_usecase,
        set_take_profit_usecase = set_take_profit_usecase,
        set_revert_limit_usecase = set_revert_limit_usecase,
        close_all_usecase = close_all_usecase,
        synchro_usecase = synchro_usecase,
        messenger_api = messenger_api,
        trading_status_interactor = trading_status_interactor,
        save_timer = save_timer,
        trading_config = trading_config,
    )

    error_handler: ErrorHandler = providers.Singleton(
        BybitErrorHandler,
        messenger = messenger_api,
    )

    event_loop: EventLoop = providers.Singleton(
        EventLoop,
    )

    request_queue: RequestTimePriorityQueue = providers.Singleton(
        RequestTimePriorityQueue,
        event_loop = event_loop
    )

    request_event_loop: RequestEventLoop = providers.Singleton(
        RequestEventLoop,
        request_queue = request_queue,
        event_loop = event_loop,
        interactor = trade_interactor,
        error_handler = error_handler,
        mapper=signal_to_intent_mapper,
    )

    signal_controller: SignalController = providers.Singleton(
        SignalController,
        messenger = messenger_api,
        logger = logger,
        trade_logger = trading_logger,
        secured_config = secured_config,
        request_queue = request_queue
    )
