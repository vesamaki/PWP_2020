"""
This module initializes the Flask instance of
    Cycling equipment usage API.

See https://github.com/vesamaki/PWP_2020 for details
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# Adapted from PWP "Flask API Project Layout" -material
# Based on:
# http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
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
    # ensure, that app.instance_path exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # Callback used to initialize an application
    # for the use with this database setup.
    db.init_app(app)
    # Models defines the init-db command, but
    # import inside this function to prevent circular imports
    from . import models
    # Register the init-db command for the Flask instance
    # Use as "flask init-db" in CMD
    app.cli.add_command(models.init_db_command)
    # API blueprint defined in api, but
    # import inside this function to prevent circular imports
    from . import api
    # Register the blueprint "api_bp" for Flask instance
    app.register_blueprint(api.api_bp)
    print(app.instance_path)  # Just to see where instance data is stored
    return app
