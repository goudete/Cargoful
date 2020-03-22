Project Layout:
The project is made up of three django apps: authorization, trucker, and shipper.

authorization contains everything related to the registering and logging in and out of users.

trucker contains everything that has to do with the trucker side

shipper contains everything that has to do with the shipper side
----
How to clone and run:
1. pull from github

2. create .env file in src directory
	- add SECRET_KEY=[insert secret key here]
	- add DEBUG=on
	- 

3. Activate virtual environment
	- go into project directory
	- type into command line: 'source venv/bin/activate'

4. Run Server
	- move into 'src' folder
	- type into command line: 'python manage.py runserver'
	- copy and paste http address returned from command line
	  into browser
----
Now that the local server is up and running, these are the current working urls:

/accounts/login
/register
/shipper
/trucker
