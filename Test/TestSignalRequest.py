import requests

url = 'http://localhost:80/position'
#url = 'http://77.232.135.88:80/position'

#"{"signal":"{{strategy.order.comment}}","token":"2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"}"

def open_short():
    print("--------SHORT TEST--------")
    data = {
        "signal": "open_short",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
    }
    response = requests.post(url, json=data)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

def open_long():
    print("--------LONG TEST--------")
    data = {
        "signal": "open_long",
        "token": "2hiKjBiVGL5LkkBKObXmQA6h4GoedZ5CYyQ7F8bOO12GES9pdTsisADIdcXUjTF2"
    }
    response = requests.post(url, json=data)
    print("Response: " + response.text)
    print("Response status code:", response.status_code)
    print("Response JSON:", str(response.json()))

