'''
This module is used to test my PWP database of app.py.
Run with:
    pytest db_tests.py
or with additional details:
    pytest db_tests.py --cov --pep8
'''

# Library imports
from datetime import datetime
from jsonschema import validate

# Project imports
from cyequ import db
from cyequ.constants import APIARY_URL
from cyequ.models import User, Equipment, Component, Ride


def _populate_db():
    '''
    We're prefixing this function and its ilk with a single underscore to
    softly hint that these are the test module's internal tools.
    '''

    # Create everything
    user1 = User(name="Joonas")
    user2 = User(name="Janne")
    equipment1 = Equipment(name="Polkuaura",
                           category="Mountain Bike",
                           brand="Kona",
                           model="HeiHei",
                           date_added=datetime(2019, 11, 21, 11, 20, 30),
                           owner=1
                           )
    equipment2 = Equipment(name="Kisarassi",
                           category="Road Bike",
                           brand="Bianchi",
                           model="Intenso",
                           date_added=datetime(2019, 11, 21, 11, 20, 30),
                           date_retired=datetime(2019, 12, 21, 11, 20, 30),
                           owner=1
                           )
    component1 = Component(name="Hissitolppa",
                           category="Seat Post",
                           brand="RockShox",
                           model="Reverb B1",
                           date_added=datetime(2019, 11, 21, 11, 20, 30),
                           equipment_id=1
                           )
    component2 = Component(name="Takatalvikiekko",
                           category="Rear Wheel",
                           brand="Sram",
                           model="Roam AL 650b",
                           date_added=datetime(2019, 11, 21, 11, 20, 30),
                           date_retired=datetime(2019, 12, 21, 11, 20, 30),
                           equipment_id=1
                           )
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(equipment1)
    db.session.add(equipment2)
    db.session.add(component1)
    db.session.add(component2)
    db.session.commit()


# Adapted from Ex3
def _get_user_json(name="Jenni"):
    '''
    Creates a valid user JSON object to be used for PUT and POST tests.
    '''

    return {"name": name}


def _get_equipment_json(name="Hyppykeppi",
                        category="Mountain Bike",
                        brand="Santa Cruz",
                        model="Tall Boy",
                        date_added="2019-11-21 11:20:30",
                        date_retired=None
                        ):
    '''
    Creates a valid equipment JSON object to be used for PUT and POST tests.
    With optional date_retired input parameter use datetime()
    '''

    if date_retired is None:
        return {"name": name,
                "category": category,
                "brand": brand,
                "model": model,
                "date_added": date_added
                }
    else:
        return {"name": name,
                "category": category,
                "brand": brand,
                "model": model,
                "date_added": date_added,
                "date_retired": date_retired
                }


def _get_component_json(name="Vauhtiheijastin",
                        category="Front Reflector",
                        brand="BBB",
                        model="Aero Reflector",
                        date_added="2019-11-21 11:20:30",
                        date_retired=None
                        ):
    '''
    Creates a valid equipment JSON object to be used for PUT and POST tests.
    With optional date_retired input parameter use datetime()
    '''

    if date_retired is None:
        return {"name": name,
                "category": category,
                "brand": brand,
                "model": model,
                "date_added": date_added
                }
    else:
        return {"name": name,
                "category": category,
                "brand": brand,
                "model": model,
                "date_added": date_added,
                "date_retired": date_retired
                }


def _check_namespace(client, response):
    '''
    Checks that the "cyequ" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed. Also check
    that redirect Location header has valid URL in APIARY.
    '''

    # Read from Json structure
    ns_href = response["@namespaces"]["cyequ"]["name"]
    # Sends a get request to name space link
    resp = client.get(ns_href)
    # Will redirect to APIARY
    assert resp.status_code == 302
    assert resp.headers["Location"] == APIARY_URL + "link-relations"


def _check_profile(ctrl, client, obj, resource):
    '''
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Checks that the profile is found from the response body,
    and that its "href" attribute is a URL that can be accessed. Also check
    that redirect Location header has valid URL in APIARY.
    '''

    # Read from Json structure
    href = obj["@controls"][ctrl]["href"]
    # Sends a get request to name space link
    resp = client.get(href)
    # Will redirect to APIARY
    assert resp.status_code == 302
    assert resp.headers["Location"] == APIARY_URL + resource


def _check_control_get_method(ctrl, client, obj):
    '''
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    '''

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    '''
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status
    code of 204.
    '''

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method(ctrl, client, obj, content):
    '''
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid content against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    '''

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = content
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj, content):
    '''
    Checks a POST type control from a JSON object be it root document or
    an item in a collection. In addition to checking the "href" attribute,
    also checks that method, encoding and schema can be found from the
    control. Also validates a valid content against the schema of the control
    to ensure that they match. Finally checks that using the control results
    in the correct status code of 201.
    '''

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = content
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


# Adapted from Ex2
# The below _get_ -functions are used by the tests to populate the database
# for db_tests.py
def _get_user(username="janne"):
    '''
    Function used to set a user instance's data
    Used by test-functions
    '''
    return User(name="user-{}".format(username))


def _get_equipment(cat="Mountain Bike", ret=False, own=1, number=1):
    '''
    Function used to set an equipment instance's data
    Used by test-functions
    '''
    if ret:
        equipout = Equipment(
                        name="Bike-{}".format(number),
                        category="{}".format(cat),
                        brand="Kona",
                        model="HeiHei",
                        date_added=datetime(2018, 11, 21, 11, 20, 30),
                        date_retired=datetime.now(),
                        owner=own
                        )
    else:
        equipout = Equipment(
                        name="Bike-{}".format(number),
                        category="{}".format(cat),
                        brand="Kona",
                        model="HeiHei",
                        date_added=datetime(2018, 11, 21, 11, 20, 30),
                        # date_retired=datetime(2019, 11, 21, 11, 20, 30),
                        owner=own
                        )
    return equipout


def _get_component(cat="Fork", ret=False, equi=1):
    '''
    Function used to set a component instance's data
    Used by test-functions
    '''
    if ret:
        compout = Component(
                        category="{}".format(cat),
                        brand="Fox",
                        model="34 Factory",
                        date_added=datetime(2018, 11, 21, 11, 20, 30),
                        date_retired=datetime.now(),
                        equipment_id=equi
                        )
    else:
        compout = Component(
                        category="{}".format(cat),
                        brand="Fox",
                        model="34 Factory",
                        date_added=datetime(2018, 11, 21, 11, 20, 30),
                        # date_retired=datetime(2019, 11, 21, 11, 20, 30),
                        equipment_id=equi
                        )
    return compout


def _get_ride(equi=1, rid=1):
    '''
    Function used to set a ride instance's data
    Used by test-functions
    '''
    return Ride(
        name="Ajo-{}".format(rid),
        duration=120,
        datetime=datetime.now(),
        equipment_id=equi,
        rider=rid
        )
