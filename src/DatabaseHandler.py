import re
import bs4
import csv
import time
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
	def saveFilmIDDatabase(imdbIDs, path):
		outputFile = open(path, 'w', newline='')
		outputWriter = csv.writer(outputFile)
		outputWriter.writerow(imdbIDs)
		outputFile.close()
	
	@staticmethod
	def __select(url, stringToMatch, useFindAll):
		soup = DatabaseHandler.__getSoup(DatabaseHandler.__getRes(url))
		
		if soup == None:
			return None
		
		if useFindAll:
			return soup.find_all(href=re.compile(stringToMatch))
		else:
			return soup.select(stringToMatch)
	
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
		
		if res == None:
			return None
		
		soup = bs4.BeautifulSoup(res.text, features="html.parser")
		res.close()
		
		return soup
	
	@staticmethod
	def __getRequest(url, requestsList):
		requestsList.append(requests.get(url))
	
	@staticmethod
	def __waitForThreads(threads):
		while len(threads) > 0:
			threads.pop().join()
	
	@staticmethod
	def generateFilmDatabase(filmIDDatabasePath):
		print('Loading films. This may take up to 25 minutes.')
		startTime = time.time()
		
		wikiLists = DatabaseHandler.__select('https://en.wikipedia.org/wiki/Lists_of_films', '/wiki/List_of_films:_(numbers|[A-Z])', True)
		imdbIDs = DatabaseHandler.__loadWikiLists(startTime, wikiLists, [0], 500)
		
		# This removes all duplicate film ids from the list
		imdbIDs = list(dict.fromkeys(imdbIDs))
		
		DatabaseHandler.saveFilmIDDatabase(imdbIDs, filmIDDatabasePath)
		
		print('Completion time: ' + str(time.time() - startTime))
	
	@staticmethod
	def __loadWikiLists(startTime, wikiLists, filmsLoaded, requestsInParallel):
		imdbIDs = []
		
		for wikiList in wikiLists:
			print(wikiList.get('title'))
			
			wikiFilms = DatabaseHandler.__select('https://en.wikipedia.org' + wikiList.get('href'), 'body ul i a', False)
			
			if wikiFilms == None:
				continue
			
			DatabaseHandler.__loadWikiFilms(startTime, imdbIDs, wikiFilms, filmsLoaded, requestsInParallel)
		
		return imdbIDs
	
	@staticmethod
	def __loadWikiFilms(startTime, imdbIDs, wikiFilms, filmsLoaded, requestsInParallel):
		count = 0
		threads = []
		loadedWikiFilmPageList = []
		
		for wikiFilm in wikiFilms:
			count += 1
			url3 = 'https://en.wikipedia.org' + wikiFilm.get('href')
			threadObject = threading.Thread(target=DatabaseHandler.__getRequest, args=[url3, loadedWikiFilmPageList])
			threads.append(threadObject)
			threadObject.start()
			
			if count % requestsInParallel == 0 or len(loadedWikiFilmPageList) >= requestsInParallel or count == len(wikiFilms):
				DatabaseHandler.__waitForThreads(threads)
				DatabaseHandler.__loadIMDBFilms(startTime, imdbIDs, loadedWikiFilmPageList, filmsLoaded)
	
	@staticmethod
	def __loadIMDBFilms(startTime, imdbIDs, loadedWikiFilmPageList, filmsLoaded):
		while len(loadedWikiFilmPageList) > 0:
			soup = DatabaseHandler.__getSoup(loadedWikiFilmPageList.pop())
			
			if soup == None:
				continue
			
			imdbFilms = soup.find_all(href=DatabaseHandler.__regex)
			DatabaseHandler.__loadIMDBFilmIDs(imdbIDs, imdbFilms, filmsLoaded)
		
		printString = '\tFilms loaded: %5d, Films loaded per second: %3.2f, Total seconds: %d'
		print(printString % (filmsLoaded[0], filmsLoaded[0] / (time.time() - startTime), time.time() - startTime))
	
	@staticmethod
	def __loadIMDBFilmIDs(imdbIDs, imdbFilms, filmsLoaded):
		for imdbFilm in imdbFilms:
			imdbID = imdbFilm.get('href')[-8:-1];
			
			if not imdbID.isdigit():
				print(imdbFilm.get('href') + ' ' + imdbFilm.text)
				continue
			
			imdbIDs.append(imdbID)
			filmsLoaded[0] += 1
