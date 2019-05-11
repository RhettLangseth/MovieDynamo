import re
import bs4
import csv
import time
import json
import requests
import threading


class DatabaseHandler:
	__regex = re.compile('^https://www.imdb.com/title/tt[^/]+/$')
	
	@staticmethod
	def loadFilmIDDatabase(path):
		inputFile = open(path)
		inputReader = csv.reader(inputFile)
		imdbIDs = list(inputReader)
		inputFile.close()
		return imdbIDs
	
	@staticmethod
	def saveDatabase(dataList, path):
		outputFile = open(path, 'w', newline='')
		outputWriter = csv.writer(outputFile)
		outputWriter.writerow(dataList)
		outputFile.close()
	
	@staticmethod
	def __select(url, stringToMatch, searchMethod):
		soup = DatabaseHandler.__getSoup(DatabaseHandler.__getRes(url))
		
		if soup is None:
			return None
		
		if searchMethod == 0:
			return soup.select(stringToMatch)
		elif searchMethod == 1:
			return soup.find_all(href=re.compile(stringToMatch))
		elif searchMethod == 2:
			return soup.find_all(attrs={'type': 'application/ld+json'})
		else:
			return None
	
	@staticmethod
	def __getRes(url):
		res = requests.get(url)
		
		if res.status_code != requests.codes.ok:
			res.close()
			return None
		
		res.raise_for_status()
		
		return res
	
	@staticmethod
	def __getSoup(res):
		
		if res is None:
			return None
		
		soup = bs4.BeautifulSoup(res.text, features="html.parser")
		res.close()
		
		return soup
	
	@staticmethod
	def __getRequest(url, requestsList):
		res = ''
		
		while res == '':
			try:
				res = requests.get(url)
				break
			except:
				print('Connection refused for "' + url + '". Trying again in 1 second.')
				time.sleep(1)
				continue
		
		requestsList.append(res)
	
	# try:
	# 	requestsList.append(requests.get(url))
	# except requests.exceptions.ConnectionError:
	# 	print('Connection refused for', url)
	
	@staticmethod
	def __waitForThreads(threads):
		while len(threads) > 0:
			threads.pop().join()
	
	@staticmethod
	def generateFilmDatabase(filmIDDatabasePath):
		print('Loading films. This may take up to 25 minutes.')
		startTime = time.time()
		
		wikiLists = DatabaseHandler.__select('https://en.wikipedia.org/wiki/Lists_of_films',
											 '/wiki/List_of_films:_(numbers|[A-Z])', 1)
		imdbIDs = DatabaseHandler.__loadWikiLists(startTime, wikiLists, [0], 500)
		
		# This removes all duplicate film ids from the list
		imdbIDs = list(dict.fromkeys(imdbIDs))
		
		DatabaseHandler.saveDatabase(imdbIDs, filmIDDatabasePath)
		
		print('Completion time: ' + str(time.time() - startTime))
	
	@staticmethod
	def __loadWikiLists(startTime, wikiLists, filmsLoadedCount, requestsInParallel):
		imdbIDs = []
		
		for wikiList in wikiLists:
			print(wikiList.get('title'))
			
			wikiFilms = DatabaseHandler.__select('https://en.wikipedia.org' + wikiList.get('href'), 'body ul i a', 0)
			
			if wikiFilms is None:
				continue
			
			DatabaseHandler.__loadWikiFilms(startTime, imdbIDs, wikiFilms, filmsLoadedCount, requestsInParallel)
		
		return imdbIDs
	
	@staticmethod
	def __loadWikiFilms(startTime, imdbIDs, wikiFilms, filmsLoadedCount, requestsInParallel):
		count = 0
		threads = []
		loadedWikiFilmPageList = []
		
		for wikiFilm in wikiFilms:
			count += 1
			url = 'https://en.wikipedia.org' + wikiFilm.get('href')
			threadObject = threading.Thread(target=DatabaseHandler.__getRequest, args=[url, loadedWikiFilmPageList])
			threads.append(threadObject)
			threadObject.start()
			
			if count % requestsInParallel == 0 or len(loadedWikiFilmPageList) >= requestsInParallel or count == len(
					wikiFilms):
				DatabaseHandler.__waitForThreads(threads)
				DatabaseHandler.__loadIMDBFilms(startTime, imdbIDs, loadedWikiFilmPageList, filmsLoadedCount)
	
	@staticmethod
	def __loadIMDBFilms(startTime, imdbIDs, loadedWikiFilmPageList, filmsLoadedCount):
		while len(loadedWikiFilmPageList) > 0:
			soup = DatabaseHandler.__getSoup(loadedWikiFilmPageList.pop())
			
			if soup is None:
				continue
			
			imdbFilms = soup.find_all(href=DatabaseHandler.__regex)
			DatabaseHandler.__loadIMDBFilmIDs(imdbIDs, imdbFilms, filmsLoadedCount)
		
		printString = '\tFilms loaded: %5d, Films loaded per second: %3.2f, Total seconds: %d'
		print(printString % (
		filmsLoadedCount[0], filmsLoadedCount[0] / (time.time() - startTime), time.time() - startTime))
	
	@staticmethod
	def __loadIMDBFilmJSONs(startTime, imdbJSONs, loadedImdbPageList):
		while len(loadedImdbPageList) > 0:
			test = loadedImdbPageList.pop()
			soup = DatabaseHandler.__getSoup(test)
			
			if soup is None:
				continue
			
			imdbFilmJsons = soup.find_all(attrs={'type': 'application/ld+json'})
			
			if len(imdbFilmJsons) == 0:
				continue
			
			filmJson = json.loads(imdbFilmJsons[0].text)
			filmType = filmJson['@type']
			
			if filmType != 'Movie':
				continue
			
			filmDict = {}
			
			DatabaseHandler.__setValue(filmDict, filmJson, 'id', 'url', regexFilter='[^\d]')
			DatabaseHandler.__setValue(filmDict, filmJson, 'name', 'name')
			DatabaseHandler.__setValue(filmDict, filmJson, 'contentRating', 'contentRating')
			DatabaseHandler.__setValue(filmDict, filmJson, 'minutes', 'duration')
			DatabaseHandler.__setValue(filmDict, filmJson, 'year', 'datePublished')
			DatabaseHandler.__setValue(filmDict, filmJson, 'ratingValue', 'aggregateRating', jsonKey2='ratingValue')
			DatabaseHandler.__setValue(filmDict, filmJson, 'ratingCount', 'aggregateRating', jsonKey2='ratingCount')
			DatabaseHandler.__setValue(filmDict, filmJson, 'genre', 'genre')
			DatabaseHandler.__setValue(filmDict, filmJson, 'actorIds', 'actor', jsonKey2='url', regexFilter='[^\d]',
									   makeList=True)
			DatabaseHandler.__setValue(filmDict, filmJson, 'directorIds', 'director', jsonKey2='url',
									   regexFilter='[^\d]', makeList=True)
			DatabaseHandler.__setValue(filmDict, filmJson, 'writerIds', 'creator', jsonKey2='url', regexFilter='[^\d]',
									   regexToMatch='nm\d+', makeList=True)
			DatabaseHandler.__setValue(filmDict, filmJson, 'companyIds', 'creator', jsonKey2='url', regexFilter='[^\d]',
									   regexToMatch='co\d+', makeList=True)
			
			m = re.search(r'P.*T((\d+)H)?((\d+)M)?((\d+)S)?', filmDict['minutes'])
			
			if m is not None:
				if m.group(2) is not None:
					hours = m.group(2)
				else:
					hours = 0
				
				if m.group(4) is not None:
					minutes = m.group(4)
				else:
					minutes = 0
				
				filmDict['minutes'] = str(int(hours) * 60 + int(minutes))
			
			m = re.search(r'\d\d\d\d', filmDict['year'])
			
			if m is not None:
				filmDict['year'] = m.group(0)
			
			if not isinstance(filmDict['genre'][0], list):
				filmDict['genre'] = [filmDict['genre']]
			
			imdbJSONs.append(filmDict)
		
		printString = '\tFilms loaded: %5d, Films loaded per second: %3.2f, Total seconds: %d'
		print(printString % (len(imdbJSONs), len(imdbJSONs) / (time.time() - startTime), time.time() - startTime))
	
	@staticmethod
	def __setValue(filmDict, filmJson, dictKey, jsonKey, jsonKey2=None, regexFilter=None, regexToMatch=None,
				   makeList=False):
		if jsonKey in filmJson:
			if jsonKey2 is not None:
				if isinstance(filmJson[jsonKey], list):
					valueList = []
					
					for element in filmJson[jsonKey]:
						if regexToMatch is not None and not re.search(regexToMatch, element[jsonKey2]):
							continue
						
						if regexFilter is not None:
							valueList.append(re.sub(regexFilter, '', element[jsonKey2]))
						else:
							valueList.append(element[jsonKey2])
					
					filmDict[dictKey] = valueList
					return
				
				jsonValue = filmJson[jsonKey][jsonKey2]
			else:
				jsonValue = filmJson[jsonKey]
			
			if regexFilter is not None:
				jsonValue = re.sub(regexFilter, '', jsonValue)
			else:
				jsonValue = jsonValue
			
			if regexToMatch is None or re.search(regexToMatch, jsonValue):
				if makeList:
					filmDict[dictKey] = [jsonValue]
				else:
					filmDict[dictKey] = jsonValue
			else:
				if makeList:
					filmDict[dictKey] = []
				else:
					filmDict[dictKey] = 'N/A'
		else:
			filmDict[dictKey] = 'N/A'
	
	@staticmethod
	def __loadIMDBFilmIDs(imdbIDs, imdbFilms, filmsLoadedCount):
		for imdbFilm in imdbFilms:
			imdbID = imdbFilm.get('href')[-8:-1]
			
			if not imdbID.isdigit():
				# print(imdbFilm.get('href') + ' ' + imdbFilm.text)
				continue
			
			imdbIDs.append(imdbID)
			filmsLoadedCount[0] += 1
	
	@staticmethod
	def __loadIMDBFilmDatabase(startTime, filmIDDatabase, requestsInParallel):
		imdbLink = 'https://www.imdb.com/title/tt'
		imdbIDs = filmIDDatabase[0]
		loadedImdbPageList = []
		imdbJSONs = []
		threads = []
		count = 0
		
		for imdbID in imdbIDs:
			count += 1
			threadObject = threading.Thread(target=DatabaseHandler.__getRequest,
											args=[imdbLink + str(imdbID), loadedImdbPageList])
			threads.append(threadObject)
			threadObject.start()
			
			if count % requestsInParallel == 0 or len(loadedImdbPageList) >= requestsInParallel or count == len(
					imdbIDs):
				DatabaseHandler.__waitForThreads(threads)
				DatabaseHandler.__loadIMDBFilmJSONs(startTime, imdbJSONs, loadedImdbPageList)
		# break
		
		return imdbJSONs
	
	@staticmethod
	def generateFilmInfoDatabase(imdbIDs, filmJsonDatabasePath):
		print('Loading films information. This may take up to 1 hour.')
		startTime = time.time()
		requestsInParallel = 100
		
		imdbFilmInfoDatabase = DatabaseHandler.__loadIMDBFilmDatabase(startTime, imdbIDs, requestsInParallel)
		
		DatabaseHandler.saveDatabase(imdbFilmInfoDatabase, filmJsonDatabasePath)
		
		print('Completion time: ' + str(time.time() - startTime))
