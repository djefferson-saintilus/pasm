- ###\ v1.0
	1. Create KeePass database (Error)
		if the database path exists, the program will always delete or replace with the new database path.

		(check if the file already exists and tell the user that there is already a db with this name)
FIXED

	2. Store password (Error)
		You can create a store password with empty require input

		- password length >= 8 minimum, db and store_password (FIXED)
		- please fill all the blanks to store password (FIXED)
		- add generate password in store_password option (FIXED)

	3. clear output after using an option ~~(OPTIONAL)~~


	4. (ADDED) only use the name to look for a db, now you can look without the dir and extension

	5. (ADDED) DELETE password option

	6. (ADDED) clear screen 

	7. set command line more user-friendly for beginners
	
	8. (ADDED) If not exist (db) directory automatic creation set


