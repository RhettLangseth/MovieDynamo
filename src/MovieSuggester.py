from DatabaseHandler import DatabaseHandler as db


class MovieElement:
	def __init__(self, name, id, score):
		self.name = name
		self.id = id
		self.score = score


class MovieSuggester:
	@staticmethod
	def __getContentRatingSimilarity(movie1, movie2):
		if movie1 == 'G':
			movie1Type = 0
		elif movie1 == 'PG':
			movie1Type = 1
		elif movie1 == 'PG-13':
			movie1Type = 2
		elif movie1 == 'R':
			movie1Type = 3
		elif movie1 == 'NC-17':
			movie1Type = 4
		else:
			return 0
		
		if movie2 == 'G':
			movie2Type = 0
		elif movie2 == 'PG':
			movie2Type = 1
		elif movie2 == 'PG-13':
			movie2Type = 2
		elif movie2 == 'R':
			movie2Type = 3
		elif movie2 == 'NC-17':
			movie2Type = 4
		else:
			return 0
		
		return (5 - abs(movie1Type - movie2Type)) / 5
	
	@staticmethod
	def __getGenreScore(likedFilm, dbFilm):
		return len(set(likedFilm['genre']) & set(dbFilm['genre'])) / len(set(likedFilm['genre']) | set(dbFilm['genre']))
	
	@staticmethod
	def __getDirectorScore(likedFilm, dbFilm):
		return len(set(likedFilm['directorIds']) & set(dbFilm['directorIds'])) / len(set(likedFilm['directorIds']) | set(dbFilm['directorIds']))
	
	@staticmethod
	def __getActorScore(likedFilm, dbFilm):
		return len(set(likedFilm['actorIds']) & set(dbFilm['actorIds'])) / len(set(likedFilm['actorIds']) | set(dbFilm['actorIds']))
	
	@staticmethod
	def __getWriterScore(likedFilm, dbFilm):
		return len(set(likedFilm['writerIds']) & set(dbFilm['writerIds'])) / len(set(likedFilm['writerIds']) | set(dbFilm['writerIds']))
	
	@staticmethod
	def __getCompanyScore(likedFilm, dbFilm):
		return len(set(likedFilm['companyIds']) & set(dbFilm['companyIds'])) / len(set(likedFilm['companyIds']) | set(dbFilm['companyIds']))
	
	@staticmethod
	def __getUserRatingScore(likedFilm, dbFilm):
		if likedFilm['ratingValue'] == 'N/A' or dbFilm['ratingValue'] == 'N/A':
			return 0
		
		return (10 - abs(float(likedFilm['ratingValue']) - float(dbFilm['ratingValue']))) / 10
	
	@staticmethod
	def __getContentRatingScore(likedFilm, dbFilm):
		return MovieSuggester.__getContentRatingSimilarity(likedFilm['contentRating'], dbFilm['contentRating'])
	
	@staticmethod
	def __getYearScore(likedFilm, dbFilm):
		if likedFilm['year'] == 'N/A' or dbFilm['year'] == 'N/A':
			return 0
		
		return (10 - abs(float(likedFilm['year']) - float(dbFilm['year']))) / 10
	
	@staticmethod
	def __scoreFilm(dbFilm, likedFilms):
		totalScore = 0
		
		for likedFilm in likedFilms:
			if dbFilm['id'] == likedFilm['id']:
				continue
			
			genreScore = MovieSuggester.__getGenreScore(likedFilm, dbFilm)
			directorScore = MovieSuggester.__getDirectorScore(likedFilm, dbFilm)
			actorScore = MovieSuggester.__getActorScore(likedFilm, dbFilm)
			writerScore = MovieSuggester.__getWriterScore(likedFilm, dbFilm)
			companyScore = MovieSuggester.__getCompanyScore(likedFilm, dbFilm)
			userRatingScore = MovieSuggester.__getUserRatingScore(likedFilm, dbFilm)
			contentRatingScore = MovieSuggester.__getContentRatingScore(likedFilm, dbFilm)
			yearScore = MovieSuggester.__getYearScore(likedFilm, dbFilm)
			totalScore += genreScore + directorScore + actorScore + writerScore + companyScore + userRatingScore + contentRatingScore + yearScore
		
		return totalScore
	
	@staticmethod
	def __getFilmInfoList(filmIds, filmInfoDatabase, orderMatters):
		likedFilmInfoList = []
		
		if not orderMatters:
			for dbFilm in filmInfoDatabase:
				if dbFilm['id'] in filmIds:
					likedFilmInfoList.append(dbFilm)
		else:
			for filmId in filmIds:
				for dbFilm in filmInfoDatabase:
					if dbFilm['id'] == filmId:
						likedFilmInfoList.append(dbFilm)
		
		return likedFilmInfoList
	
	@staticmethod
	def getFilmObjects(filmsPath, filmInfoDatabase, orderMatters):
		filmIds = db.loadDatabase(filmsPath)[0]
		
		return MovieSuggester.__getFilmInfoList(filmIds, filmInfoDatabase, orderMatters)
	
	@staticmethod
	def getTopSuggestedFilms(likedFilmsPath, filmInfoDatabasePath, maxCount):
		filmInfoDatabase = db.loadFilmInfoDatabase(filmInfoDatabasePath)
		likedFilms = MovieSuggester.getFilmObjects(likedFilmsPath, filmInfoDatabase, False)
		filmInfoDatabaseScoreList = []
		
		for dbFilm in filmInfoDatabase:
			score = MovieSuggester.__scoreFilm(dbFilm, likedFilms)
			m = MovieElement(dbFilm['name'], dbFilm['id'], score)
			filmInfoDatabaseScoreList.append(m)
		
		filmInfoDatabaseScoreList.sort(key=lambda x: x.score, reverse=True)
		filmInfoDatabaseScoreList = filmInfoDatabaseScoreList[:maxCount]
		suggestedFilms = []
		
		for movieObject in filmInfoDatabaseScoreList:
			suggestedFilms.append(movieObject.id)
		
		return suggestedFilms
