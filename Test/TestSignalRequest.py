import json

import requests

#url = 'http://localhost:8000'
#url = 'https://77.232.135.88/position'
#url = 'https://werrewq-cryptobot-719a.twc1.net'
#url = 'https://werrewq-cryptobot-6169.twc1.net' # Quail
#url = 'https://werrewq-cryptobot-cba7.twc1.net' # Bittern
url = 'https://werrewq-cryptobot-3af0.twc1.net' # Taurus

# jsonData = '{"signal": "open_long", "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"}'
# alert(jsonData)

# strategy.entry("SELL", strategy.short, comment="open_short")
# jsonData = '{"signal": "open_short", "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"}'

# strategy.exit('Exit Long', 'Long', stop = stoplossLine)
# price = str.tostring(2.1)
# jsonData = '{"signal": "stop_loss", "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2", "side":"' + side + '", "stop_price":"' + price + '"}'
# alert(jsonData)

# тейк профит по маркету
# strategy.close('Long', comment = "take profit", qty_percent = takeProfitPercent)
# jsonData = '{"signal": "stop_loss", "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2", "side":"' + side + '", "trigger_price":"' + price + '", "take_profit_percentage":"' + percentage + '", "market":"True"}'
# alert(jsonData)

# close all
# jsonData = '{"signal": "close_all", "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"}'
# alert(jsonData)

# Заголовки запроса
headers = {
    "Content-Type": "application/json"
}

def open_short():
    print("--------SHORT TEST--------")
    data = json.dumps({
        "signal": "open_short",
        "timestamp": "1234561",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
        "side": side,
        "trigger_price": str(stop_price),
        "take_profit_percentage_from_order": str(take_profit_percentage),
        "market": True
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def set_revert_limit(stop_price: float, side: str):
    print("--------STOP LOSS TEST--------")
    data = json.dumps({
        "signal": "revert_limit",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
        "side": side,
        "stop_price": str(stop_price),
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def close_all():
    print("--------CLOSE ALL--------")
    data = json.dumps({
        "signal": "close_all",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
    })
    response = requests.post(url + "/position", json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def download_logs():
    print("--------DOWNLOAD_LOGS--------")
    data = json.dumps({
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
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