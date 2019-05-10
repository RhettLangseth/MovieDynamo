import requests
import json


movie = input("What's a movie you like: ")

url = "https://api.themoviedb.org/3/search/movie?include_adult=false&query=" + movie + "&language=en-US&api_key=d85618974402c12dd65393c379cfe785"

payload = "{}"
response = requests.request("GET", url, data=payload)

data = response.json()

id = (data['results'][0]['id'])

url = "https://api.themoviedb.org/3/movie/" + str(id) + "/similar?api_key=d85618974402c12dd65393c379cfe785&language=en-US&page=1"

payload = "{}"
response = requests.request("GET", url, data=payload)

data = response.json()

total = 0

for i in data['results']:
    if i['vote_average'] > 7.5:
        total += 1
        print ("\n" + i['title'] + "\n")

if total == 0:
    print ("\nI didn't find any good movies like that one.\n")
