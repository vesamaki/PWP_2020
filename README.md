# PWP SPRING 2020
# Cyclist equipment usage API
# Group information
* Student 1. Vesa Mäki and vesa.maki@student.lut.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

**NOTES**

-- Timezoning.
When POSTing data over API to backend, require client timezone info in request body?

When providing time data to a request, tell also the timezone (stored as UTC in database). Client can then convert as needed and deal with daylight saving time as well.

***TODO:***
    docstrings to all.




#### Setting up environment ####

This project followed Oulu University's Programmable Web Project course's guides. A detailed guide on how to set up the environment can be found from [Lovelace](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2020/pwp-setting-up-python-environment-for-exercises/).

Essentially, all the libraries and dependencies are listed in the requirements.txt. To set up your environment with these, run:  
__pip install -r pwp_requirements.txt__

#### Running Flask ####  
On Windows set the environment variable FLASK_APP to point to file API_flask_db.py -file. This can be done in command prompt, by browsing to folder containing the file and typing command:  
set FLASK_APP=API_flask_db.py

Then run flask with command:  
flask run

Initialize the database by running app_init.py.

Database tests are included in db_tests.py. Using this sort of testing does not require data to exist in the database.
