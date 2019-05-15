# MovieDyanmo

> Note: Compatible with Python 3 (tested on 3.6 and 3.7)

### Purpose

The goal of the MovieDynamo program is to essentially provide an API that receives information from the user and returns a list of suggested films. The way this typically works is that the user inputs a list of movies that they like. 

### Usage

```python
# create a list of suggested films
python MovieDynamo.py suggestFilms inputFile.json

# print the list of suggested films
python MovieDynamo.py printSuggestions inputFile.json
```

### How it works

The database that contains information on about 30 thousand movies is generated by using 500 threads to web scrape Wikipedia using `bs4` and find a list of links to IMDb pages. All duplicates are removed and the final list contains only the 7 digit IMDb ID numbers that can used to access the corresponding IMDb page for each film. For example, the ID number for Star Wars V is 0080684 and the url for the IMDb page is https://www.imdb.com/title/tt0080684/. This list of id numbers is saved to a file called "idDatabase.csv" and is then used to web scrape information in JSON format for each movie from IMDb. Only 100 threads are run at once to accomplish this. Each JSON is stripped of unnecessary information in order to save space. The final database is saved to a file called "infoDatabase.csv". This entire process takes around 2 hours however only needs to run one time to generate it. The user can specify their own alternate names for these files.

### Updating the database

The IMDB database can be updated as follows (takes approx 40 minutes)

```python
python MovieDynamo.py updateIdDatabase inputFile.json
```

The full database can be updated after updating the IMDB ID database as follows (takes approx 80 minutes)

```python
python MovieDynamo.py updateInfoDatabase inputFile.json
```
