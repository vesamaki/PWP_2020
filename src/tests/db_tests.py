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
from cyequ.models import User, Equipment, Component, Ride


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
              "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
              "TESTING": True
              }

    app = create_app(config)

    with app.app.app_context():
        app.db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_fname)

# Adapted from Ex2
# The below _get_ -functions are used by the tests to populate the database
def _get_user(username="janne"):
    """
    Function used to set a user instance's data
    Used by test-functions
    """
    return User(
        name="user-{}".format(username)
    )


def _get_equipment(cat="Mountain Bike", ret=False, own=1, number=1):
    """
    Function used to set an equipment instance's data
    Used by test-functions
    """
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
    """
    Function used to set a component instance's data
    Used by test-functions
    """
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
    """
    Function used to set a ride instance's data
    Used by test-functions
    """
    return Ride(
        name="Ajo-{}".format(rid),
        duration=120,
        datetime=datetime.now(),
        equipment_id=equi,
        rider=rid
        )


def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    user = _get_user()
    equipment = _get_equipment()
    component = _get_component()
    ride = _get_ride()
    # Connect relationships (just one side)
    equipment.ownedBy = user
    component.installedTo = equipment
    ride.riddenWith = equipment
    ride.riddenBy = user
    # Put to database
    db_handle.session.add(user)
    db_handle.session.add(equipment)
    db_handle.session.add(component)
    db_handle.session.add(ride)
    db_handle.session.commit()

    # Check that everything exists
    assert User.query.count() == 1
    assert Equipment.query.count() == 1
    assert Component.query.count() == 1
    assert Ride.query.count() == 1
    db_user = User.query.first()
    db_equipment = Equipment.query.first()
    db_component = Component.query.first()
    db_ride = Ride.query.first()

    # Check all relationships (both sides)
    # One to one
    assert db_user == db_ride.riddenBy
    assert db_equipment == db_ride.riddenWith
    # Others
    assert db_equipment in db_user.hasEquip
    assert db_component in db_equipment.hasCompos


def test_user_query_mod_del(db_handle):
    """
    Tests the querying of a user instance
    """
    # Query
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    user1 = User.query.filter_by(name="user-janne").first()
    assert user1.name == "user-janne"


def test_user_mod(db_handle):
    """
    Tests the modification of user instance data
    """
    # Modify
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    user = User.query.filter_by(name="user-janne").first()
    user.name = "user-joonas"
    db_handle.session.commit()
    user = User.query.filter_by(name="user-joonas").first()
    assert user.name == "user-joonas"


def test_user_del(db_handle):
    """
    Tests the deletion of a user instance
    """
    # Delete
    user = _get_user()
    db_handle.session.add(user)
    db_handle.session.commit()
    user = User.query.filter_by(name="user-janne").first()
    db_handle.session.delete(user)
    db_handle.session.commit()
    assert User.query.count() == 0


def test_equipment_query(db_handle):
    """
    Tests the querying of a equipment instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.commit()
    equip1 = Equipment.query.filter_by(name="Bike-1").first()
    assert equip1.name == "Bike-1"


def test_equipment_mod(db_handle):
    """
    Tests the modification of equipment instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.commit()
    equip = Equipment.query.get(1)
    equip.name = "Bike-2"
    equip.brand = "Canyon"
    equip.model = "Spectral"
    equip.date_added = datetime(2019, 11, 21, 11, 20, 30)
    equip.date_retired = datetime(2020, 1, 1, 11, 20, 30)
    db_handle.session.commit()
    equip = Equipment.query.get(1)
    assert equip.name == "Bike-2"
    assert equip.brand == "Canyon"
    assert equip.model == "Spectral"
    assert str(equip.date_added) == "2019-11-21 11:20:30"
    assert str(equip.date_retired) == "2020-01-01 11:20:30"


def test_equipment_del(db_handle):
    """
    Tests the deletion of a equipment instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.commit()
    equip = Equipment.query.get(1)
    db_handle.session.delete(equip)
    db_handle.session.commit()
    assert Equipment.query.count() == 0


def test_component_query(db_handle):
    """
    Tests the querying of a component instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(component)
    db_handle.session.commit()
    component1 = Component.query.filter_by(brand="Fox").first()
    assert component1.brand == "Fox"


def test_component_mod(db_handle):
    """
    Tests the modification of component instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(component)
    db_handle.session.commit()
    component.name = "Ekakeula"
    component.brand = "Rock Shox"
    component.model = "Pike RTC3"
    component.date_added = datetime(2019, 11, 21, 11, 20, 30)
    component.date_retired = datetime(2020, 1, 1, 11, 20, 30)
    db_handle.session.commit()
    component = Component.query.filter_by(category="Fork").first()
    assert component.name == "Ekakeula"
    assert component.brand == "Rock Shox"
    assert component.model == "Pike RTC3"
    assert str(component.date_added) == "2019-11-21 11:20:30"
    assert str(component.date_retired) == "2020-01-01 11:20:30"


def test_component_del(db_handle):
    """
    Tests the deletion of a component instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(component)
    db_handle.session.commit()
    component = Component.query.get(1)
    db_handle.session.delete(component)
    db_handle.session.commit()
    assert Component.query.count() == 0


def test_ride_query(db_handle):
    """
    Tests the querying of a ride instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(ride)
    db_handle.session.commit()
    ride1 = Ride.query.filter_by(name="Ajo-1").first()
    assert ride1.name == "Ajo-1"


def test_ride_mod(db_handle):
    """
    Tests the modification of ride instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(ride)
    db_handle.session.commit()
    ride.name = "Ajo-2"
    ride.duration = 1200
    ride.datetime = datetime(2020, 1, 1, 11, 20, 30)
    db_handle.session.commit()
    ride = Ride.query.get(1)
    assert ride.name == "Ajo-2"
    assert ride.duration == 1200
    assert str(ride.datetime) == "2020-01-01 11:20:30"


def test_ride_del(db_handle):
    """
    Tests the deletion of a ride instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    db_handle.session.add(user)
    db_handle.session.add(equip)
    db_handle.session.add(ride)
    db_handle.session.commit()
    db_handle.session.delete(ride)
    db_handle.session.commit()
    assert Ride.query.count() == 0


def test_ride_equipment_one_to_one(db_handle):
    """
    Tests that the relationship between ride and equipment is one-to-one.
    i.e. that one ride cannot be ridden with more than one equipment.
    """

    ride = _get_ride()
    equipment_1 = _get_equipment(number=1)
    equipment_2 = _get_equipment(number=2)
    equipment_1.inRide = ride
    equipment_2.inRide = ride
    db_handle.session.add(ride)
    db_handle.session.add(equipment_1)
    db_handle.session.add(equipment_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()


def test_equipment_ondelete_user(db_handle):
    """
    Tests that equipments's owner foreign key is set to null
    when the user is deleted.
    """

    equipment = _get_equipment()
    user = _get_user()
    equipment.ownedBy = user
    db_handle.session.add(equipment)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.commit()
    assert equipment.owner is None


def test_component_ondelete_equipment(db_handle):
    """
    Tests that components are deleted when parent equipment is deleted.
    """

    user = _get_user()
    equipment = _get_equipment()
    component = _get_component()
    component.owner = user
    component.installedTo = equipment
    db_handle.session.add(user)
    db_handle.session.add(component)
    db_handle.session.commit()
    db_handle.session.delete(equipment)
    db_handle.session.commit()
    assert Component.query.count() == 0


def test_user_columns(db_handle):
    """
    Tests user columns' restrictions. Name must be unique and mandatory.
    """

    # Uniqueness of name
    user_1 = _get_user()
    user_2 = _get_user()
    db_handle.session.add(user_1)
    db_handle.session.add(user_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null
    user = _get_user()
    user.name = None
    db_handle.session.add(user)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()


def test_equipment_columns(db_handle):
    """
    Tests equipment columns' restrictions. Name must be unique.
    Name, category, brand, model and date_added must be mandatory.
    Date_added and date_retired must be type datetime and owner accepts
    only numerical values.
    Date_added must be less than date_retired.
    """

    # Uniqueness of name
    equip_1 = _get_equipment()
    equip_2 = _get_equipment()
    db_handle.session.add(equip_1)
    db_handle.session.add(equip_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null name
    equipment = _get_equipment()
    equipment.name = None
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null category
    equipment = _get_equipment()
    equipment.category = None
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null brand
    equipment = _get_equipment()
    equipment.brand = None
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null model
    equipment = _get_equipment()
    equipment.model = None
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null date_added
    equipment = _get_equipment()
    equipment.date_added = None
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type int owner
    equipment = _get_equipment()
    equipment.owner = str(equipment.owner) + "kg"
    db_handle.session.add(equipment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type datetime date_added
    equipment = _get_equipment()
    equipment.date_added = time.time()
    db_handle.session.add(equipment)
    with pytest.raises(StatementError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type datetime date_retired
    equipment = _get_equipment()
    equipment.date_retired = time.time()
    db_handle.session.add(equipment)
    with pytest.raises(StatementError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # date_retired greater than date_added
    equipment = _get_equipment()
    equipment.date_added = datetime.now()
    equipment.date_retired = datetime(2020, 1, 1, 0, 0, 0)
    db_handle.session.add(equipment)
    with pytest.raises(StatementError):
        db_handle.session.commit()


def test_component_columns(db_handle):
    """
    Tests component columns' restrictions. Category, brand, model and
    date_added must be mandatory. Date_added and date_retired must be type
    datetime and equipment_id accepts only numerical values.
    """

    # Uniqueness of category
    component_1 = _get_component()
    component_2 = _get_component()
    db_handle.session.add(component_1)
    db_handle.session.add(component_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null category
    component = _get_component()
    component.name = None
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null category
    component = _get_component()
    component.category = None
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null brand
    component = _get_component()
    component.brand = None
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null model
    component = _get_component()
    component.model = None
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null date_added
    component = _get_component()
    component.date_added = None
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type int equipment_id
    component = _get_component()
    component.equipment_id = str(component.equipment_id) + "kg"
    db_handle.session.add(component)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type datetime date_added
    component = _get_component()
    component.date_added = time.time()
    db_handle.session.add(component)
    with pytest.raises(StatementError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # date_retired greater than date_added
    component = _get_component()
    component.date_added = datetime.now()
    component.date_retired = datetime(2020, 1, 1, 0, 0, 0)
    db_handle.session.add(component)
    with pytest.raises(StatementError):
        db_handle.session.commit()


def test_ride_columns(db_handle):
    """
    Tests that columns duration and datetime are mandatory.
    Tests that duration value only accepts integer values and that
    datetime only accepts datetime values.
    """

    # Uniqueness of name
    ride_1 = _get_ride()
    ride_2 = _get_ride()
    db_handle.session.add(ride_1)
    db_handle.session.add(ride_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null name
    ride = _get_ride()
    ride.name = None
    db_handle.session.add(ride)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null duration
    ride = _get_ride()
    ride.duration = None
    db_handle.session.add(ride)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Not null datetime
    ride = _get_ride()
    ride.datetime = None
    db_handle.session.add(ride)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type int duration
    ride = _get_ride()
    ride.duration = str(ride.duration) + "kg"
    db_handle.session.add(ride)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # Type datetime
    ride = _get_ride()
    ride.datetime = time.time()
    db_handle.session.add(ride)
    with pytest.raises(StatementError):
        db_handle.session.commit()

    db_handle.session.rollback()

    # duration greater than zero
    ride = _get_ride()
    ride.duration = 0
    db_handle.session.add(ride)
    with pytest.raises(StatementError):
        db_handle.session.commit()
