import os
import sys
import DatabaseHandler


def printUsage():
	print('Usage: python MovieDynamo.py idDatabase.csv likedFilms.csv dislikedFilms.csv recommendedFilms.csv')
	sys.exit(1)


# python MovieDynamo.py idDatabase.csv likedFilms.csv dislikedFilms.csv recommendedFilms.csv

if len(sys.argv) != 5:
	printUsage()

for i in range(1, 5):
	if not os.path.splitext(sys.argv[i])[1] == '.csv':
		printUsage()

if not os.path.isfile(sys.argv[2]) or not os.path.isfile(sys.argv[3]):
	printUsage()

if not os.path.exists(os.path.dirname(os.path.abspath(sys.argv[4]))):
	printUsage()

filmIDDatabasePath = sys.argv[1]
likedFilmsPath = sys.argv[2]
dislikedFilmsPath = sys.argv[3]
recommendedFilmsPath = sys.argv[4]

# filmIDDatabase = DatabaseHandler.DatabaseHandler.loadFilmIDDatabase(filmIDDatabasePath)
# filmIDDatabase[0].sort()  # Fix this: Some ids are invalid
# print(str(len(filmIDDatabase[0])))
# print(filmIDDatabase)

DatabaseHandler.DatabaseHandler.generateFilmDatabase(filmIDDatabasePath)
