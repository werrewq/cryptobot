import requests

url = 'http://127.0.0.1:5000/position'
data = {
    "signal": "open_short",
    "price": 100.5
}

response = requests.post(url, json=data)
print("Response: " + response.text)

print("Response status code:", response.status_code)
print("Response JSON:", str(response.json()))