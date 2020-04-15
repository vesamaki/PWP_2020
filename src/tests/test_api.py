"""
This module is used to test my PWP database of app.py.
Run with:
    pytest db_tests.py
or with additional details:
    pytest db_tests.py --cov --pep8
"""

import os
import tempfile
import time
from datetime import datetime
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from cyequ import create_app, db
from cyequ.constants import MASON, USER_PROFILE, EQUIPMENT_PROFILE, \
                            COMPONENT_PROFILE, ERROR_PROFILE, \
                            LINK_RELATIONS_URL, APIARY_URL
from cyequ.models import User, Equipment, Component  # , Ride

from tests.utils import _get_user, _get_equipment, _get_component, _get_ride


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
              "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
              "TESTING": True
              }
    # Create app to be used in testing with this fixture
    app = create_app(config)
    # Must be used for all db opertations
    with app.app_context():
        db.create_all()
        _populate_db()
    # Generates the app for any caller of this fixture
    yield app.test_client()
    # After caller finishes, the rest after yield are executed
    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    '''
    We're prefixing this function and its ilk with a single underscore to
    softly hint that these are the test module's internal tools.
    '''

    # Create everything
    user = _get_user()
    equipment = _get_equipment()
    component = _get_component()
    ride = _get_ride()
    db.session.add(user)
    db.session.add(equipment)
    db.session.add(component)
    db.session.add(ride)
    db.session.commit()

    class TestUserCollection(object):
        
