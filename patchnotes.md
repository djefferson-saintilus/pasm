v1.0
- add generate password in store_password option
- encrypted password when enter in db and show entries options
don't show password field, ever gonna show it, show the encrypted
version for password


- ###\ v1.1
	1. Create KeePass database (Error)
		if the database path exists, the program will always delete or replace with the new database path.

		(Fix)
		(check if the file already exists and tell the user that there is already a db with this name)

	2. Store password (Error)
		You can create a store password with empty require input

		(Fix)
		- entry name, username, password and website URL can not empty 
		- password length >= 8
	3.

	4.

	5.





