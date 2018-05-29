import requests
from project.log import logger

print("This program is still in developments phase")

while (1):
    print("Enter a user id")
    user_id = input("> ")
    print("Enter beverage id")
    beverage_id = input("> ")


    payload = {'user_id': user_id, 'beverage_id': beverage_id}
    response = requests.post('http://127.0.0.1:5000/api/buy_beverage', params=payload)
    print(response.url)
    print(response.text)
