import requests

url = 'http://localhost:8080/position'


def open_short():
    print("--------SHORT TEST--------")
    data = {
        "signal": "open_short",
        "price": 100.5
    }
    response = requests.post(url, json=data)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def open_long():
    print("--------LONG TEST--------")
    data = {
        "signal": "open_long",
        "price": 100.5
    }
    response = requests.post(url, json=data)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

