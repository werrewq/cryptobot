from typing import Any

from bot.domain.ErrorHandler import ErrorHandler
from bot.domain.MessengerApi import MessengerApi
from bot.domain.TradeInteractor import TradeInteractor
from bot.presentation.SignalToIntentMapper import SignalToIntentMapper
from bot.presentation.worker.EventLoop import EventLoop
from bot.presentation.worker.RequestTimePriorityQueue import RequestTimePriorityQueue
import threading
import asyncio
import logging
import traceback

class RequestEventLoop:

    __interactor: TradeInteractor
    __error_handler: ErrorHandler
    __mapper: SignalToIntentMapper
    __messenger: MessengerApi

    def __init__(
            self,
            request_queue: RequestTimePriorityQueue,
            event_loop: EventLoop,
            interactor: TradeInteractor,
            messenger: MessengerApi,
            error_handler: ErrorHandler,
            mapper: SignalToIntentMapper
    ):
        self.__request_queue = request_queue
        self.__loop = event_loop.loop
        self.thread = threading.Thread(target=self.__start_event_loop, daemon=True)
        self.__interactor = interactor
        self.__error_handler = error_handler
        self.__messenger = messenger
        self.__mapper = mapper

    def start(self):
        self.thread.start()

    def __start_event_loop(self):
        asyncio.set_event_loop(self.__loop)
        # Запускаем основную задачу обработки запросов
        self.__loop.create_task(self.__process_requests())
        # Запускаем цикл
        self.__loop.run_forever()

    async def __process_requests(self):
        while True:
            try:
                # Выполняем все запросы накопившиеся за секунду
                if not self.__request_queue.is_empty():
                    data = await self.__request_queue.poll_oldest_request()
                    # Обрабатываем запрос
                    await self.__handle_request(data)
                else:
                    # Если очередь пуста, делаем паузу
                    await asyncio.sleep(1)
            except Exception as e:
                logging.error(
                    msg="Ошибка на RequestEventLoop: \n"
                    + repr(e)
                    + "\n"
                    + str(traceback.format_exc())
                )

    async def __handle_request(self, data: dict[str, Any]):
        time = data["timestamp"]
        # Тут логика обработки запроса
        logging.debug(f"Обработка запроса: time:{time}\n{str(data)}")

        self.__messenger.send_message("Signal from TRADING VIEW \n" + str(data["signal"]))
        self.__error_handler.handle(lambda: self.process_signal(data))

    def process_signal(self, json_data):
        intent = self.__mapper.map(json_data)
        self.__interactor.start_trade(intent)
