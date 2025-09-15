import json

import requests

url = 'your_hosting_url'

# jsonData = '{"signal": "open_long", "token": "your_bot_token"}'
# alert(jsonData)

# price = str.tostring(2.1)
# jsonData = '{"signal": "stop_loss", "token": "your_bot_token", "side":"' + side + '", "stop_price":"' + price + '"}'
# alert(jsonData)

# strategy.entry("SELL", strategy.short, comment="open_short")
# jsonData = '{"signal": "open_short", "token": "your_bot_token"}'

# Заголовки запроса
headers = {
    "Content-Type": "application/json"
}

def open_short():
    print("--------SHORT TEST--------")
    data = json.dumps({
        "signal": "open_short",
        "timestamp": "1234561",
        "token": "your_bot_token"
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def open_long():
    print("--------LONG TEST--------")
    data = json.dumps({
        "signal": "open_long",
        "timestamp": "1234562",
        "token": "your_bot_token"
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def set_stop_loss(stop_price: float, side: str):
    print("--------STOP LOSS TEST--------")
    data = json.dumps({
        "signal": "stop_loss",
        "timestamp": "1234563",
        "token": "your_bot_token",
        "side": side,
        "stop_price": str(stop_price),
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def set_take_profit(stop_price: float, side: str, take_profit_percentage: int):
    print("--------TAKE_PROFIT_TEST--------")
    data = json.dumps({
        "signal": "take_profit",
        "timestamp": "1234564",
        "token": "your_bot_token",
        "side": side,
        "trigger_price": str(stop_price),
        "take_profit_percentage_from_order": str(take_profit_percentage),
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def set_take_profit_market(stop_price: float, side: str, take_profit_percentage: int):
    print("--------STOP LOSS TEST--------")
    data = json.dumps({
        "signal": "take_profit",
        "timestamp": "1234565",
        "token": "your_bot_token",
        "side": side,
        "trigger_price": str(stop_price),
        "take_profit_percentage_from_order": str(take_profit_percentage),
        "market": True
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def download_logs():
    print("--------DOWNLOAD_LOGS--------")
    data = json.dumps({
        "token": "your_bot_token",
    })
    # download_headers = {
    #     "Content-Type": "text/plain",
    #     "Content - Disposition": "attachment; filename = \"logs.txt\""
    # }
    response = requests.post(url + "/logs", json=data, headers= headers)
    if response.status_code == 200:
        # Сохранение файла
        with open('bot_logs.txt', 'wb') as f:
            f.write(response.content)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)

def download_trade_logs():
    print("--------DOWNLOAD_TRADE_LOGS--------")
    data = json.dumps({
        "token": "your_bot_token",
    })
    response = requests.post(url + "/trading_logs", json=data, headers= headers)
    if response.status_code == 200:
        # Сохранение файла
        with open('trading_logs.txt', 'wb') as f:
            f.write(response.content)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)

def try_200():
    response = requests.post(url = url + "/")
    print("Response: " + response.text)
    print("Response status code:", response.status_code)