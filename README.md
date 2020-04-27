# PWP SPRING 2020
# Cyclist equipment usage API
# Group information
* Student 1. Vesa Mäki and vesa.maki@student.lut.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

**NOTES**

-- Timezoning.
When POSTing data over API to backend, require client timezone info in request body?

When providing time data to a request, tell also the timezone (stored as UTC in database). Client can then convert as needed and deal with daylight saving time as well.

### TODO: ###
#####    docstrings to all. #####

##### Create json schemas for Models. **Done** #####
    Put to static folder. **Done**  
    Figure out format. **Done. Will be a .py file** with content as in Ex3 schema function
    Importing to app. **Import module as normal**

##### Component UniqueConstraints not working #####

##### What to put in __init__.py of resources -folder #####    

##### Fix db_tests.py according to new project structure **Done** #####

##### Do API implementation tests **Done** #####

##### FOR CLIENT: Reading ISO 8601 datetime format #####  
I.e: "2019-11-21T10:20:30"  
Might help: [StackOveflow](https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date)  

##### Test cloning, setup and running #####
Revise instructions here

### Setting up environment ###

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

Then run flask with command:  
__flask run__

#### Running Tests ####
Database tests are included in .\\tests\\test_db.py.  
API-tests are in .\\tests\\api_test.py.  
Using this sort of testing does not require Flask to run, or even data to exist in the database.  
Change directory to your project folder. Both tests can be run with command:  
__pytest ./src/tests/ --cov=./src/cuequ/ --cov-report term-missing__

**NOTE ON TEST COVERAGE**  
For some reason, test_api.py tests won't cover many of the error responses even though they are asserted. I.e. test_api.py lines test 197-203 should cover user.py missing line 155 of coverage report. Most of the missing lines have the same problem, though I didn't write tests for all after noticing the coverage behavior of above example.
