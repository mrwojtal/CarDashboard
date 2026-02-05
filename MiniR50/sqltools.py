import sqlite3

def database_query(query, action = None):
	"""
	Function used to connect to database and commit transaction to database, one at a time.
	Function was created to avoid issues with recursive use of cursors.
	:param query: query to execute in SQL
	:param action: if 'SELECT' then function returns response
	:return: if action == 'SELECT' function returns transaction response, else function returns None.
	"""
	#connect to database
	dbConnection = sqlite3.connect("/miniDB.db", check_same_thread=False)
	
	#create cursor for queries to database
	dbCursor = dbConnection.cursor()
	
	#execute given query
	response = dbCursor.execute(query)
	
	if action == 'SELECT':
		to_return = str(response.fetchone())
		to_return = to_return[1:-2] #needed to remove () brackets and , delimeter
		if to_return.find("'") != -1:
			to_return = to_return.replace("'", "") #needed for VARCHAR type response
	
	#commit transaction to database
	dbConnection.commit()
	
	#close connection to database
	dbConnection.close()
	
	#return value if select query was called
	if action == 'SELECT':
		return to_return
	else:
		return None
