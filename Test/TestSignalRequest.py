import json

import requests

#url = 'https://localhost:8000/position'
#url = 'https://77.232.135.88/position'
url = 'https://werrewq-cryptobot-719a.twc1.net/position'

#"{"signal":"{{strategy.order.comment}}","token":"2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"}"

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
    response = requests.post(url, json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def open_long():
    print("--------LONG TEST--------")
    data = json.dumps({
        "signal": "open_long",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
    })
    response = requests.post(url, json=data, headers= headers)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def try_200():
    response = requests.post(url = 'http://werrewq-cryptobot-719a.twc1.net/')
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))