import logging
import asyncio
from asyncio import PriorityQueue
from typing import Any
from bot.presentation.worker.EventLoop import EventLoop


class RequestTimePriorityQueue:
    __request_queue: PriorityQueue

    def __init__(self, event_loop: EventLoop):
        self.__request_queue = asyncio.PriorityQueue()
        self.__event_loop = event_loop.loop
        logging.debug("EventLoop init")

    def add_request(self, json_request_data: dict[str, Any]):
        # Это синхронная функция для добавления запроса в очередь
        # Используем run_coroutine_threadsafe для вызова асинхронной put_request из другого потока
        asyncio.run_coroutine_threadsafe(
            self.__put_request(json_request_data),
            self.__event_loop
        )

    async def __put_request(self, json_request_data: dict[str, Any]):
        time_data = (json_request_data["timestamp"],json_request_data)
        logging.debug(f"put request time = {time_data[0]},\ndata = {time_data[1]}")
        await self.__request_queue.put(time_data)

    async def poll_oldest_request(self) -> dict[str, Any]:
        time, data = await self.__request_queue.get()
        logging.debug(f"poll request time = {time},\ndata = {data}")
        return data

    def is_empty(self) -> bool:
        return self.__request_queue.empty()