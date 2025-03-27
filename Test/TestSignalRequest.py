import json

import requests

url = 'http://localhost:8000'
#url = 'https://77.232.135.88/position'
#url = 'https://werrewq-cryptobot-719a.twc1.net/position'

# {"signal":"{{strategy.order.comment}}","token":"2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2","side":"{{strategy.order.action}}"}

# alert("{" +
#           "\"action\": \"set_stop_loss\"," +
#           "\"stop_loss\": " + str.tostring(stopLossPrice) + "," +
#           "\"entry_price\": " + str.tostring(close) +
#           "}", alert.freq_once_per_bar)

# Заголовки запроса
headers = {
    "Content-Type": "application/json"
}

def open_short():
    print("--------SHORT TEST--------")
    data = json.dumps({
        "signal": "open_short",
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
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2",
        "side": side,
        "stop_price": str(stop_price),
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