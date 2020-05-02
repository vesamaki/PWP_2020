"""
This module initializes the Flask instance of
    Cycling equipment usage API.

See https://github.com/vesamaki/PWP_2020 for details
"""

# Library imports
import os
from datetime import datetime
from flask import Flask
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy

# Project imports
# --

db = SQLAlchemy()


# Custom JSONEncoder for converting dates to ISO 8601
# Curtesy of StackOverflow:
# https://stackoverflow.com/questions/43663552/keep-a-datetime-date-in-yyyy-mm-dd-format-when-using-flasks-jsonify  # noqa: E501
class CustomJSONEncoder(JSONEncoder):
    '''
    This class defines a custom JSONEncoder subclass to control the format of
    jsonify with datetime-objects.
    '''
    def default(self, obj):
        if isinstance(obj, datetime):
            # Produces a string, i.e. 2020-04-30T12:18:00,
            # when database datetime-objects are jsonified by JSONEncoder.
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


# Adapted from PWP "Flask API Project Layout" -material
# Based on:
# http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    '''
    Creates and returns the API flask application instance.
    '''

    # Create Flask instance with name as set by FLASK_APP variable
    app = Flask(__name__,
                static_folder="static",
                instance_relative_config=True)
    # Configure the instance functionality
    app.config.from_mapping(
        SECRET_KEY="dev",   # Used by Flask and extensions to keep data safe
        # Path to database file
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path,
                                                            "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    # Optionally set Flask instance config from test_config or from file.
    # if config.py is given, then it overrides the above default configuration
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    # Ensure, that app.instance_path exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # Callback used to initialize an application
    # for the use with this database setup.
    db.init_app(app)
    # Models defines the init-db command, but
    # import inside this function to prevent circular imports
    from cyequ import models
    # Register the init-db command for the Flask instance
    # Use as "flask init-db" in CMD
    app.cli.add_command(models.init_db_command)
    # Register the testgen command for the Flask instance
    # Use as "flask testgen" in CMD
    app.cli.add_command(models.add_test_data)
    # API blueprint defined in api, but
    # import inside this function to prevent circular imports
    from cyequ import api
    # Register the blueprint "api_bp" for Flask instance
    app.register_blueprint(api.api_bp)
    # Use CustomJSONEndcoder
    app.json_encoder = CustomJSONEncoder
    # print(app.instance_path)  # Just to see where instance data is stored
    return app
