import json
from time import sleep

from bot.presentation.worker.EventLoop import EventLoop
from bot.presentation.worker.RequestEventLoop import RequestEventLoop
from bot.presentation.worker.RequestTimePriorityQueue import RequestTimePriorityQueue
from unittest.mock import Mock

event_loop = EventLoop()
queue = RequestTimePriorityQueue(event_loop)
request_loop = RequestEventLoop(queue, event_loop, Mock(), Mock(), Mock())


request1 = {
    "signal": "open_long",
    "timestamp": "1234561",
    "token": "your_bot_token"
}

request2 = {
    "signal": "open_short",
    "timestamp": "1234562",
    "token": "your_bot_token"
}

request3 = {
    "signal": "open_long",
    "timestamp": "1234563",
    "token": "your_bot_token"
}

data = json.dumps({
    "signal": "open_long",
    "token": "your_bot_token"
})

if __name__ == '__main__':
    request_loop.start()
    sleep(2)
    queue.add_request(request3)
    queue.add_request(request2)
    queue.add_request(request1)
    sleep(2)
    queue.add_request(request3)
    queue.add_request(request2)
    queue.add_request(request1)
    sleep(2)
