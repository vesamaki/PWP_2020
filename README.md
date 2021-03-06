# PWP SPRING 2020
# Cyclist equipment usage API
# Group information
* Student 1. Vesa Mäki and vesa.maki@student.lut.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

**NOTES**

-- Timezoning.
When POSTing data over API to backend, require client timezone info in request body?

When providing time data to a request, tell also the timezone (stored as UTC in database). Client can then convert as needed and deal with daylight saving time as well.

### API external library dependencies: ###
Flask >= 1.0.2  
Flask-RESTful >= 0.3.7  
Flask-SQLAlchemy >= 2.3.2  
SQLAlchemy >= 1.3.1  
Click >= 7.0  
jsonschema >= 3.0.1  
pytest >= 5.4.1  
pytest-cov >= 2.8.1  
requests >= 2.23.0  

These will be installed if the environment is setup according to the following section.

### Setting up API environment ###

This project followed Oulu University's Programmable Web Project course's guides.  
Essentially, these steps:
<ul>
<li>Create a folder for the project and clone this repo into it. </li>
<li>Create a virtual environment folder within, i.e. my\\project\\folder\\venv</li>
<li>Install virtualenv to manage all Python dependencies for the project</li>  
On Windows: python.exe -m pip install virtualenv
<li>Then create the virtual environment</li>  
python.exe -m venv /path/to/new/virtual/environment
<li>And activate the environment</li>  
venv\Scripts\activate.bat
</ul>

A detailed guide on how to set up the environment can be found from [Lovelace](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2020/pwp-setting-up-python-environment-for-exercises/).

After this the project can be installed in editable mode so that you don't need to reinstall it whenever you make changes. You use pip to install it, and add the -e option. In the folder where the setup.py is, run:

__pip install -e .__

#### Running Flask ####  
On Windows set the environment variable FLASK_APP to point to project package. This can be done in command prompt, by browsing to the your project folder and typing command:  
__set FLASK_APP=cyequ__  
__set FLASK_ENV=development__  

Setup the database:  
__flask init-db__

The database can be populated with test data using command:
__flask testgen__

Then run flask with command:  
__flask run__

#### Running Tests ####
Database tests are included in .\\tests\\test_db.py.  
API-tests are in .\\tests\\api_test.py.  
Using this sort of testing does not require Flask to run, or even data to exist in the database.  
Change directory to your project folder. Both tests can be run with command:  
__pytest ./src/tests/ --cov=./src/cuequ/ --cov-report term-missing__

Regarding main errors I detected thanks to functional testing, where should I begin? The testing was a multiday exercise and frankly I no longer remember (after two weeks now when writing this) what were the most significant or reoccurring errors. I just remember having to make corrections a lot. The testing did remind me of adding checks to the code for things such as date_retired not being in the future of date_added.

**NOTE ON TEST COVERAGE**  
For some reason, test_api.py tests won't cover many of the error responses even though they are asserted. I.e. test_api.py lines test 197-203 should cover user.py missing line 155 of coverage report. Most of the missing lines have the same problem, though I didn't write tests for all after noticing the coverage behavior of above example.

### API-client external library dependencies: ###
requests >= 2.23.0  

This will be installed if the environment is setup according to the following section.

### Setting up API-client environment ###
The API client can be run in an instance of the API virtual environment. Alternatively, you can create a separate virtual environment and use the requirements.txt in your-project-folder/API-client/ to install all required dependencies for the client.   Create and activate the client virtual environment.  
Then change directory to ./API-client/  
Run command:  
__pip install -r requirements.txt__

#### Running Client ####  
The client is a command line app.  
Use the command line to change directory to ./API-client. Then run the app by typing __app.py__.

If the API is run on the localhost loopback (127.0.0.1:5000), then the URL to access the API is:  
__http://localhost:5000/api/__
