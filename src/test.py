import requests
import json

movie = input("What's a movie you like? ")

url = "https://api.themoviedb.org/3/search/movie?include_adult=false&query=" + movie + "&language=en-US&api_key=d85618974402c12dd65393c379cfe785"

payload = "{}"
response = requests.request("GET", url, data=payload)

data = response.json()

id = (data['results'][0]['id'])

url = "https://api.themoviedb.org/3/movie/" + str(id) + "/similar?api_key=d85618974402c12dd65393c379cfe785&language=en-US&page=1"

payload = "{}"
response = requests.request("GET", url, data=payload)

data = response.json()

print ("Here are some movies you might like!\n")

print (data['results'][0]['title'] + "\n")

print (data['results'][1]['title'] + "\n")

print (data['results'][2]['title'])
