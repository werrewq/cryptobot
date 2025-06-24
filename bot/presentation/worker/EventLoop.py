import asyncio


class EventLoop:

    def __init__(self):
        self.loop = asyncio.new_event_loop()