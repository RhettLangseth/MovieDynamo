from src.DatabaseHandler import DatabaseHandler as db

filmIDDatabase = db.loadFilmIDDatabase('idDatabase.csv')
db.generateFilmInfoDatabase(filmIDDatabase, 'infoDatabase.csv')
