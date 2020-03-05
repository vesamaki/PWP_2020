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
