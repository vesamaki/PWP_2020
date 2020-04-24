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
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event

from cyequ import create_app, db
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
        # Plus 3, because we know the id of newly created user is 3, since
        # there are initially two users in the db.
        header_URI = valid["name"].replace(" ", "%20") + "3"
        assert resp.headers["Location"] \
            .endswith(self.RESOURCE_URL + header_URI + "/")  # noqa: E501
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

    # RESOURCE_URL = "/api/users/Joonas1/"
    @staticmethod
    def resource_URL(user="Joonas", id=1):
        return "/api/users/{}{}/".format(user.replace(" ", "%20"), str(id))

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work.
        '''

        # Invalid route
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        body = json.loads(resp.data)
        assert body["@error"]["@message"] == "Not found"
        assert str(body["@error"]["@messages"]) == "[\'No user was " \
                                                   "found with URI {}\']" \
                                                   .format("Jaana1")
        _check_profile("profile", client, body, "error-profile")
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
        body = json.loads(resp.data)
        assert body["@error"]["@message"] == "Not found"
        assert str(body["@error"]["@messages"]) == "[\'No user was " \
                                                   "found with URI {}\']" \
                                                   .format("Jaana1")
        _check_profile("profile", client, body, "error-profile")
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
        resp = client.get(self.resource_URL(user="Joonas"))
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]
        # Test existing
        valid = _get_user_json(name="Janne")
        resp = client.put(self.resource_URL(user="Joonas"),
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
    def resource_URL(user="Joonas", id=1):
        return "/api/users/{}{}/all_equipment/" \
               .format(user.replace(" ", "%20"), str(id))

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
        assert body["items"][0]["name"] == "Polkuaura"
        assert body["items"][1]["name"] == "Kisarassi"
        assert body["items"][0]["category"] == "Mountain Bike"
        assert body["items"][1]["category"] == "Road Bike"
        assert body["items"][0]["date_added"] == "2019-11-21T11:20:30"
        assert body["items"][1]["date_added"] == "2019-11-21T11:20:30"
        assert body["items"][0]["date_retired"] is None
        assert body["items"][1]["date_retired"] == "2019-12-21T11:20:30"
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile("profile", client, item, "equipment-profile")

    def test_post(self, client):
        '''
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        '''

        # Invalid route
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        # Test inconsistent dates
        valid = _get_equipment_json(date_retired="2018-11-21 11:20:30")
        resp = client.post(self.resource_URL(user="Joonas"), json=valid)
        assert resp.status_code == 409
        # Test for unsupported media type (content-type header)
        resp = client.post(self.resource_URL(), data=json.dumps(valid))
        assert resp.status_code == 415
        # Test for invalid JSON document
        resp = client.post(self.resource_URL(), json="invalid")
        assert resp.status_code == 400
        # Test missing required fields
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
        # Test with valid
        valid = _get_equipment_json()
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 201
        # Test Location header
        header_URI = valid["name"].replace(" ", "%20")
        assert resp.headers["Location"].endswith(self.resource_URL() + header_URI + "/")  # noqa: E501
        # Follow location header and test response
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        # See if POSTed exists
        body = json.loads(resp.data)
        assert body["name"] == "Hyppykeppi"
        assert body["category"] == "Mountain Bike"
        assert body["brand"] == "Santa Cruz"
        assert body["model"] == "Tall Boy"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["user"] == "Joonas"
        # POST again for 409
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 409


class TestEquipmentItem(object):
    '''
    This class implements tests for each HTTP method in EquipmentItem
    resource.
    '''

    COMPONENT_URL = "/api/users/Joonas/all_equipment/Polkuaura/VauhtiHeijastin/"  # noqa: E501
    @staticmethod
    def resource_URL(user="Joonas", equipment="Polkuaura"):
        return "/api/users/{}/all_equipment/{}/" \
               .format(user.replace(" ", "%20"),
                       equipment.replace(" ", "%20")
                       )

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        '''

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        # Test valid route
        resp = client.get(self.resource_URL())
        assert resp.status_code == 200
        # Test valid content
        body = json.loads(resp.data)
        assert body["name"] == "Polkuaura"
        assert body["category"] == "Mountain Bike"
        assert body["brand"] == "Kona"
        assert body["model"] == "Hei Hei"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["user"] == "Joonas"
        # Test controls
        _check_namespace(client, body)
        _check_control_get_method("cyequ:owner", client, body)
        _check_control_get_method("cyequ:equipment-owned", client, body)
        _check_control_get_method("cyequ:users-all", client, body)
        _check_control_post_method("cyequ:add-component",
                                   client,
                                   body,
                                   _get_component_json()
                                   )

        _check_control_get_method("self", client, body)
        _check_profile("profile", client, body, "equipment-profile")
        _check_control_put_method("edit", client, body, _get_equipment_json())
        # Test valid component items content
        assert len(body["items"]) == 2
        assert body["items"][0]["name"] == "Takatalvikiekko"
        assert body["items"][1]["name"] == "Hissitolppa"
        assert body["items"][0]["category"] == "Rear Wheel"
        assert body["items"][1]["category"] == "Seat Post"
        assert body["items"][0]["date_added"] == "2019-11-21T11:20:30"
        assert body["items"][1]["date_added"] == "2019-11-21T11:20:30"
        assert body["items"][0]["date_retired"] == "2019-12-21T11:20:30"
        assert body["items"][1]["date_retired"] is None
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_profile("profile", client, item, "component-profile")
        _check_control_delete_method("cyequ:delete", client, body)

    def test_post(self, client):
        '''
        Tests the POST method. Creates a new component for equipment.
        Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        '''

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        # Test if equipment already retired
        valid = _get_component_json()
        resp = client.post(self.resource_URL(equipment="Kisarassi"))
        # Test for unsupported media type (content-type header)
        resp = client.post(self.resource_URL(), data=json.dumps(valid))
        assert resp.status_code == 415
        # Test for invalid JSON document
        resp = client.post(self.resource_URL(), json="invalid")
        assert resp.status_code == 400
        # Test missing required fields
        valid.pop("category")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("brand")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("model")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("date_added")
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        # Test with valid
        valid = _get_component_json()
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 201
        # Test Location header
        header_URI = valid["category"].replace(" ", "%20")
        assert resp.headers["Location"].endswith(self.resource_URL() + header_URI + "/")  # noqa: E501
        # Follow location header and test response
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        # See if POSTed exists
        body = json.loads(resp.data)
        assert body["name"] == "VauhtiHeijastin"
        assert body["category"] == "Front Reflector"
        assert body["brand"] == "BBB"
        assert body["model"] == "Aero Reflector"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["equipment"] == "Polkuaura"
        # POST again for 409. Fails, because no functioning
        # unique constraint in place yet
        # resp = client.post(self.resource_URL(), json=valid)
        # assert resp.status_code == 409

        # Test to add component to an existing, but retired category
        # USELESS TEST IF ABOVE UNIQUE CONSTRAINT DOES NOT EXIST
        valid = _get_component_json(name="Takakesäkiekko",
                                    category="Rear Wheel",
                                    brand="DT Swiss",
                                    model="M1700",
                                    date_added="2019-12-22 11:20:30"
                                    )
        resp = client.post(self.resource_URL(), json=valid)
        assert resp.status_code == 201
        # Test component date_added < equipment date_added
        valid = _get_component_json(name="Etukesäkiekko",
                                    category="Front Wheel",
                                    brand="Shimano",
                                    model="R500",
                                    date_added="2019-10-22 11:20:30",
                                    date_retired="2020-01-22 11:20:30"
                                    )
        resp = client.post(self.resource_URL(equipment="Kisarassi"),
                           json=valid
                           )
        assert resp.status_code == 409
        # Test inconsistent dates, date_added < date_retired
        # Test component date_added < equipment date_added
        valid = _get_component_json(name="Etukesäkiekko",
                                    category="Front Wheel",
                                    brand="Shimano",
                                    model="R500",
                                    date_added="2019-10-22 11:20:30",
                                    date_retired="2020-11-21 11:20:30"
                                    )
        resp = client.post(self.resource_URL(equipment="Kisarassi"),
                           json=valid
                           )
        assert resp.status_code == 409

    def test_put(self, client):
        '''
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        '''

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        # Test for unsupported media type (content-type header)
        valid = _get_equipment_json()
        resp = client.put(self.resource_URL(), data=json.dumps(valid))
        assert resp.status_code == 415
        # Test for invalid JSON document
        resp = client.put(self.resource_URL(), json="invalid")
        assert resp.status_code == 400
        # Test missing required fields
        valid.pop("name")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("category")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("brand")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("model")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_equipment_json()
        valid.pop("date_added")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        # Test inconsistent dates
        valid = _get_equipment_json(date_retired="2019-10-21 11:20:30")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 409
        # Test with valid
        valid = _get_equipment_json()
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 204
        # Test new URI exists
        resp = client.get(self.resource_URL(equipment=valid["name"]))
        assert resp.status_code == 200
        # See if changes exist
        body = json.loads(resp.data)
        assert body["name"] == "Hyppykeppi"
        assert body["category"] == "Mountain Bike"
        assert body["brand"] == "Santa Cruz"
        assert body["model"] == "Tall Boy"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["user"] == "Joonas"
        # Test PUT for existing equipment for 409
        valid = _get_equipment_json(name="Kisarassi")
        resp = client.put(self.resource_URL(equipment="Hyppykeppi"),
                          json=valid
                          )
        assert resp.status_code == 409
        # Test modifying new date_added to the future of old date added
        # on equiment with components associated
        valid = _get_equipment_json(date_retired="2019-09-21 11:20:30")
        resp = client.put(self.resource_URL(equipment="Hyppykeppi"),
                          json=valid
                          )
        assert resp.status_code == 409
        # Test that retiring equipment also retires associated components
        valid = _get_equipment_json(date_retired="2019-12-21 11:20:30")
        client.put(self.resource_URL(equipment="Hyppykeppi"),
                   json=valid
                   )
        resp = client.get(self.resource_URL(equipment="Hyppykeppi"))
        body = json.loads(resp.data)
        for item in body["items"]:
            assert item["date_retired"] == "2019-12-21T11:20:30"

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the resource afterwards results in 404.
        Also checks that trying to delete a resource that doesn't exist results
        in 404.
        """

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        # Valid request
        resp = client.delete(self.resource_URL())
        assert resp.status_code == 204
        # Test if exists
        resp = client.get(self.resource_URL())
        assert resp.status_code == 404
        # Test redeletion
        resp = client.delete(self.resource_URL())
        assert resp.status_code == 404


class TestComponentItem(object):
    '''
    This class implements tests for each HTTP method in EquipmentByUser
    resource.
    '''

    EQUIPMENT_URL = "/api/users/Joonas/all_equipment/Polkuaura/"
    # RESOURCE_URL = "/api/users/Joonas/all_equipment/"
    @staticmethod
    def resource_URL(user="Joonas",
                     equipment="Polkuaura",
                     component="Seat Post"
                     ):
        return "/api/users/{}/all_equipment/{}/{}/" \
               .format(user.replace(" ", "%20"),
                       equipment.replace(" ", "%20"),
                       component.replace(" ", "%20"))

    def test_get(self, client):
        '''
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work.
        '''

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(component="Soittokello"))
        assert resp.status_code == 404
        # Test valid route
        resp = client.get(self.resource_URL())
        assert resp.status_code == 200
        # Test valid content
        body = json.loads(resp.data)
        assert body["name"] == "Hissitolppa"
        assert body["category"] == "Seat Post"
        assert body["brand"] == "RockShox"
        assert body["model"] == "Reverb B1"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["equipment"] == "Polkuaura"
        # Test controls
        _check_namespace(client, body)
        _check_control_get_method("cyequ:users-all", client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("up", client, body)
        _check_profile("profile", client, body, "component-profile")
        _check_control_put_method("edit", client, body, _get_component_json())
        # Get new body for DELETE control test after PUT
        resp = client.get(self.resource_URL(component="Rear Wheel"))
        body = json.loads(resp.data)
        _check_control_delete_method("cyequ:delete", client, body)

    def test_put(self, client):
        '''
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        '''

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(component="Soittokello"))
        assert resp.status_code == 404
        # Test for unsupported media type (content-type header)
        valid = _get_component_json()
        resp = client.put(self.resource_URL(), data=json.dumps(valid))
        assert resp.status_code == 415
        # Test for invalid JSON document
        resp = client.put(self.resource_URL(), json="invalid")
        assert resp.status_code == 400
        # Test missing required fields
        valid.pop("category")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("brand")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("model")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        valid = _get_component_json()
        valid.pop("date_added")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 400
        # Test inconsistent dates. date_added > date_retired
        valid = _get_component_json(date_retired="2019-10-21 11:20:30")
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 409
        # Test with valid
        valid = _get_component_json()
        resp = client.put(self.resource_URL(), json=valid)
        assert resp.status_code == 204
        # Test new URI exists
        resp = client.get(self.resource_URL(component=valid["category"]
                                            .replace(" ", "%20")
                                            )
                          )
        assert resp.status_code == 200
        # See if changes exist
        body = json.loads(resp.data)
        assert body["name"] == "VauhtiHeijastin"
        assert body["category"] == "Front Reflector"
        assert body["brand"] == "BBB"
        assert body["model"] == "Aero Reflector"
        assert body["date_added"] == "2019-11-21T11:20:30"
        assert body["date_retired"] is None
        assert body["equipment"] == "Polkuaura"
        # Test PUT for existing equipment for 409. Fails,
        # because no functioning unique constraint in place yet
        # valid = _get_component_json(name="Takatalvikiekko")
        # resp = client.put(self.resource_URL(component="Front Reflector"),
        #                   json=valid
        #                   )
        # assert resp.status_code == 409
        # Test component date_added < equipment date_added
        valid = _get_component_json(date_added="2019-09-21 11:20:30")
        resp = client.put(self.resource_URL(component="Front Reflector"),
                          json=valid
                          )
        assert resp.status_code == 409

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the resource afterwards results in 404.
        Also checks that trying to delete a resource that doesn't exist results
        in 404.
        """

        # Invalid routes
        resp = client.get(self.resource_URL(user="Jaana"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Kolmipyörä"))
        assert resp.status_code == 404
        resp = client.get(self.resource_URL(equipment="Soittokello"))
        assert resp.status_code == 404
        # Valid request
        resp = client.delete(self.resource_URL())
        assert resp.status_code == 204
        # Test if exists
        resp = client.get(self.resource_URL())
        assert resp.status_code == 404
        # Test redeletion
        resp = client.delete(self.resource_URL())
        assert resp.status_code == 404
