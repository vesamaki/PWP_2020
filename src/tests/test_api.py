'''
This module is used to test my PWP database of app.py.
Run with:
    pytest db_tests.py
or with additional details:
    pytest db_tests.py --cov --pep8
'''

import json
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
# from cyequ.models import User, Equipment, Component  # , Ride

from tests.utils import _get_user_json, _get_equipment_json, \
                        _get_component_json, _check_namespace, _check_profile, \
                        _check_control_get_method, \
                        _check_control_delete_method, \
                        _check_control_put_method, \
                        _check_control_post_method, \
                        _populate_db


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
    os.close(db_fd)
    os.unlink(db_fname)


class TestEntry(object):
    '''
    This class implements tests for API Entry Point GET method
    in Entry resource.
    '''

    RESOURCE_URL = "/api/"

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work.
        '''
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        # Store body of response to body
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("cyequ:users-all", client, body)


class TestUserCollection(object):
    '''
    This class implements tests for each HTTP method in UserCollection
    resource.
    '''

    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB population are present, and their controls.
        '''

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_post_method("cyequ:add-user",
                                   client,
                                   body,
                                   _get_user_json()
                                   )
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile("profile", client, item, "user-profile")
            assert "name" in item

    def test_post(self, client):
        '''
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        '''

        valid = _get_user_json()
        # Test for unsupported media type (content-type header)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        # Test for invalid JSON document
        resp = client.post(self.RESOURCE_URL, json="invalid")
        assert resp.status_code == 400
        # Remove required fields
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        # Test with valid
        valid = _get_user_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        # Test Location header
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")  # noqa: E501
        # Follow location header and test response
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        # See if POSTed exists
        body = json.loads(resp.data)
        assert body["name"] == "Jenni"
        # POST again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409


class TestUserItem(object):
    '''
    This class implements tests for each HTTP method in EquipmentByUser
    resource.
    '''

    # RESOURCE_URL = "/api/users/Joonas/"
    @staticmethod
    def resource_URL(user="Joonas"):
        return "/api/users/{}/".format(user)

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work.
        '''

        # Invalid route
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        # Valid route ./Joonas/
        resp = client.get(self.resource_URL(user="Joonas"))
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Joonas"
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_profile("profile", client, body, "user-profile")
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body, _get_user_json())
        _check_control_get_method("cyequ:equipment-owned", client, body)

    def test_put(self, client):
        '''
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        '''

        # Invalid route
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        # Valid route ./Joonas/ -> ./Jenni/
        valid = _get_user_json()
        # Test for unsupported media type (content-type header)
        resp = client.put(self.resource_URL(user="Joonas"),
                          data=json.dumps(valid)
                          )
        assert resp.status_code == 415
        # Tests for invalid JSON document
        resp = client.put(self.resource_URL(user="Joonas"), json="invalid")
        assert resp.status_code == 400
        # Remove required fields
        valid.pop("name")
        resp = client.put(self.resource_URL(user="Joonas"), json=valid)
        assert resp.status_code == 400
        # Test with valid content
        valid = _get_user_json()
        resp = client.put(self.resource_URL(user="Joonas"),
                          json=valid
                          )
        assert resp.status_code == 204
        # Test changed
        resp = client.get(self.resource_URL(user="Jenni"))
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]
        # Test existing
        valid = _get_user_json(name="Janne")
        resp = client.put(self.resource_URL(user="Jenni"),
                          json=valid
                          )
        assert resp.status_code == 409


class TestEquipmentByUser(object):
    '''
    This class implements tests for each HTTP method in EquipmentByUser
    resource.
    '''

    # RESOURCE_URL = "/api/users/Joonas/all_equipment/"
    @staticmethod
    def resource_URL(user="Joonas"):
        return "/api/users/{}/all_equipment/".format(user)

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        '''

        # Invalid route
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        # Valid route
        resp = client.get(self.resource_URL(user="Joonas"))
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("cyequ:owner", client, body)
        _check_control_post_method("cyequ:add-equipment",
                                   client,
                                   body,
                                   _get_equipment_json()
                                   )
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile("profile", client, item, "equipment-profile")
        assert body["items"][0]["name"] == "Polkuaura"
        assert body["items"][1]["name"] == "Kisarassi"
        assert body["items"][0]["category"] == "Mountain Bike"
        assert body["items"][1]["category"] == "Road Bike"
        assert body["items"][0]["date_added"] == "Thu, 2019-11-21 11:20:30 GMT"
        # assert body["items"][1]["date_added"] == "2019-11-21 11:20:30"
        assert body["items"][0]["date_retired"] is None
        # assert body["items"][1]["date_retired"] == "2019-12-21 11:20:30"

    def test_post(self, client):
        '''
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        '''

        valid = _get_equipment_json()
        valid.pop("category")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("brand")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("model")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("date_added")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400


class TestEquipmentItem(object):
    '''
    This class implements tests for each HTTP method in EquipmentItem
    resource.
    '''

    # RESOURCE_URL = "/api/users/Joonas/all_equipment/"
    @staticmethod
    def resource_URL(user="Joonas", equipment="Polkuaura"):
        return "/api/users/{}/all_equipment/{}/".format(user, equipment)

    pass


class TestComponentItem(object):
    '''
    This class implements tests for each HTTP method in EquipmentByUser
    resource.
    '''

    pass
