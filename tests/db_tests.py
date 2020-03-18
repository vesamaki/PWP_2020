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

import app
from app import User, Equipment, Component, Ride


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
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True

    with app.app.app_context():
        app.db.create_all()

    yield app.db

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _get_user(username="janne"):
    return User(
        name="user-{}".format(username)
    )


def _get_equipment(cat="Mountain Bike", ret=False, own=1, number=1):
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
