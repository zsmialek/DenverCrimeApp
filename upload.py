import pandas as pd
import pg8000
import getpass
import os

login = raw_input('Login: ')
secret = getpass.getpass('password: ')

credentials = {'user' : login,
		'password' : secret,
		'database' : 'csci403',
		'host' : 'flowers.mines.edu'}

try:
	db = pg8000.connect(**credentials)
except pg8000.Error as e:
	print('Database error: ', e.args[2])
	exit()
db.autocommit = True
cursor = db.cursor()

delStatment = "DROP TABLE IF EXISTS crime"

try:
	cursor.execute(delStatment)
	
except pg8000.Error as e:
	
	print('Database error drop table: ', e.args[2])	

createTable = 'CREATE TABLE crime()'

try:
	cursor.execute(createTable)

except pg8000.Error as e:
	print('Data error creating table: ', e.args[2])
	exit()

print "Tabled Created \n"

print "Reading csv file \n"

data = pd.read_csv("crime.csv", nrows=1)

for colName in data:
	try:
		addColStatement = "ALTER TABLE crime ADD COLUMN " + colName + " text"
		cursor.execute(addColStatement)

	except pg8000.Error as e:
		print('Database error altering table: ', e.args[2])

	print "created column: " + colName

copy = "COPY crime from " + "\'crime.csv" + "\'" + " DELIMITER \',\' CSV HEADER" 

print "Copy Statment: " + copy

#try:
	#cursor.execute(copy)
#except pg8000.Error as e:
	#print ('Error in copying from file: ', e.args[2])

cursor.close()
db.close() 
