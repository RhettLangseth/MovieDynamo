from src.DatabaseHandler import DatabaseHandler as db

filmIDDatabase = db.loadDatabase('idDatabase.csv')
db.generateFilmInfoDatabase(filmIDDatabase, 'infoDatabase.csv')
