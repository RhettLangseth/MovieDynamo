import os
import sys
import json
from DatabaseHandler import DatabaseHandler as db
from MovieSuggester import MovieSuggester as ms


def printUsage():
	print('Usage: python MovieDynamo.py [Command] [Input File Name]')
	print('Commands:')
	print('\tsuggestFilms       [Input_File_Name.json]')
	print('\tupdateIdDatabase   [Input_File_Name.json]')
	print('\tupdateInfoDatabase [Input_File_Name.json]')
	print('\tprintSuggestions   [Input_File_Name.json]')
	sys.exit(1)


def printSuggestions(outputFilePath, filmInfoDatabasePath):
	filmInfoDatabase = db.loadFilmInfoDatabase(filmInfoDatabasePath)
	filmInfoDatabaseScoreList = ms.getFilmObjects(outputFilePath, filmInfoDatabase)
	i = 0
	
	for film in filmInfoDatabaseScoreList:
		i += 1
		print(str(i) + ':\t[tt' + film['id'] + '] ' + film['name'])


def run():
	if len(sys.argv) < 3:
		printUsage()
	
	command = sys.argv[1]
	inputFilePath = sys.argv[2]
	
	if not os.path.isfile(inputFilePath):
		print(inputFilePath, 'could not be found.')
		sys.exit(1)
	
	with open(inputFilePath) as json_file:
		data = json.load(json_file)
		filmIdDatabasePath = data['filmIdDatabase']
		filmInfoDatabasePath = data['filmInfoDatabase']
		likedFilmsPath = data['likedFilms']
		dislikedFilmsPath = data['dislikedFilms']
		outputFilePath = data['outputFile']
		maxCount = int(data['count'])
	
	fileNotFound = False
	
	if command == 'updateIdDatabase' and not os.path.isfile(filmIdDatabasePath):
		fileNotFound = True
		print(filmIdDatabasePath, 'could not be found.')
	
	if (command == 'suggestFilms' or command == 'printSuggestions') and not os.path.isfile(filmInfoDatabasePath):
		fileNotFound = True
		print(filmInfoDatabasePath, 'could not be found.')
	
	if command == 'suggestFilms' and not os.path.isfile(likedFilmsPath):
		fileNotFound = True
		print(likedFilmsPath, 'could not be found.')
	
	# I may use films that are disliked by the user in the future to make suggestions
	# if not os.path.isfile(dislikedFilmsPath):
	# 	fileNotFound = True
	# 	print(dislikedFilmsPath, 'could not be found.')
	
	if command == 'printSuggestions' and not os.path.isfile(outputFilePath):
		fileNotFound = True
		print(outputFilePath, 'could not be found.')
	
	if fileNotFound:
		sys.exit(1)
	
	if command == 'suggestFilms':
		print('Making suggestions, please wait. This should only take a few seconds.')
		suggestedFilms = ms.getTopSuggestedFilms(likedFilmsPath, filmInfoDatabasePath, maxCount)
		db.saveDatabase(suggestedFilms, outputFilePath)
		print('Done! Suggestions were saved to ' + outputFilePath + '.')
	elif command == 'updateIdDatabase':
		db.generateFilmDatabase(filmIdDatabasePath)
	elif command == 'updateInfoDatabase':
		filmIdDatabase = db.loadDatabase(filmIdDatabasePath)
		db.generateFilmInfoDatabase(filmIdDatabase, filmInfoDatabasePath)
	elif command == 'printSuggestions':
		printSuggestions(outputFilePath, filmInfoDatabasePath)
	else:
		printUsage()


run()
# python MovieDynamo.py suggestFilms inputFile.json
# python MovieDynamo.py updateIdDatabase inputFile.json
# python MovieDynamo.py updateInfoDatabase inputFile.json
