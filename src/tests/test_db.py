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
from tests.utils import _get_user, _get_equipment, _get_component, _get_ride


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Adapted from Ex2
# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    # Create tempfile to store test db
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
    # Generates the app for any caller of this fixture
    yield app
    # After caller finishes, the rest after yield are executed
    os.close(db_fd)
    os.unlink(db_fname)


def test_create_instances(app):
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
    with app.app_context():
        db.session.add(user)
        db.session.add(equipment)
        db.session.add(component)
        db.session.add(ride)
        db.session.commit()

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


def test_user_query_mod_del(app):
    """
    Tests the querying of a user instance
    """
    # Query
    user = _get_user()
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        user1 = User.query.filter_by(name="user-janne").first()
        assert user1.name == "user-janne"


def test_user_mod(app):
    """
    Tests the modification of user instance data
    """
    # Modify
    user = _get_user()
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(name="user-janne").first()
        user.name = "user-joonas"
        db.session.commit()
        user = User.query.filter_by(name="user-joonas").first()
        assert user.name == "user-joonas"


def test_user_del(app):
    """
    Tests the deletion of a user instance
    """
    # Delete
    user = _get_user()
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(name="user-janne").first()
        db.session.delete(user)
        db.session.commit()
        assert User.query.count() == 0


def test_equipment_query(app):
    """
    Tests the querying of a equipment instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.commit()
        equip1 = Equipment.query.filter_by(name="Bike-1").first()
        assert equip1.name == "Bike-1"


def test_equipment_mod(app):
    """
    Tests the modification of equipment instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.commit()
        equip = Equipment.query.get(1)
        equip.name = "Bike-2"
        equip.brand = "Canyon"
        equip.model = "Spectral"
        equip.date_added = datetime(2019, 11, 21, 11, 20, 30)
        equip.date_retired = datetime(2020, 1, 1, 11, 20, 30)
        db.session.commit()
        equip = Equipment.query.get(1)
        assert equip.name == "Bike-2"
        assert equip.brand == "Canyon"
        assert equip.model == "Spectral"
        assert str(equip.date_added) == "2019-11-21 11:20:30"
        assert str(equip.date_retired) == "2020-01-01 11:20:30"


def test_equipment_del(app):
    """
    Tests the deletion of a equipment instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.commit()
        equip = Equipment.query.get(1)
        db.session.delete(equip)
        db.session.commit()
        assert Equipment.query.count() == 0


def test_component_query(app):
    """
    Tests the querying of a component instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(component)
        db.session.commit()
        component1 = Component.query.filter_by(brand="Fox").first()
        assert component1.brand == "Fox"


def test_component_mod(app):
    """
    Tests the modification of component instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(component)
        db.session.commit()
        component.name = "Ekakeula"
        component.brand = "Rock Shox"
        component.model = "Pike RTC3"
        component.date_added = datetime(2019, 11, 21, 11, 20, 30)
        component.date_retired = datetime(2020, 1, 1, 11, 20, 30)
        db.session.commit()
        component = Component.query.filter_by(category="Fork").first()
        assert component.name == "Ekakeula"
        assert component.brand == "Rock Shox"
        assert component.model == "Pike RTC3"
        assert str(component.date_added) == "2019-11-21 11:20:30"
        assert str(component.date_retired) == "2020-01-01 11:20:30"


def test_component_del(app):
    """
    Tests the deletion of a component instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    component = _get_component()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(component)
        db.session.commit()
        component = Component.query.get(1)
        db.session.delete(component)
        db.session.commit()
        assert Component.query.count() == 0


def test_ride_query(app):
    """
    Tests the querying of a ride instance
    """
    # Query
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(ride)
        db.session.commit()
        ride1 = Ride.query.filter_by(name="Ajo-1").first()
        assert ride1.name == "Ajo-1"


def test_ride_mod(app):
    """
    Tests the modification of ride instance data
    """
    # Modify
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(ride)
        db.session.commit()
        ride.name = "Ajo-2"
        ride.duration = 1200
        ride.datetime = datetime(2020, 1, 1, 11, 20, 30)
        db.session.commit()
        ride = Ride.query.get(1)
        assert ride.name == "Ajo-2"
        assert ride.duration == 1200
        assert str(ride.datetime) == "2020-01-01 11:20:30"


def test_ride_del(app):
    """
    Tests the deletion of a ride instance
    """
    # Delete
    user = _get_user()
    equip = _get_equipment()
    ride = _get_ride()
    with app.app_context():
        db.session.add(user)
        db.session.add(equip)
        db.session.add(ride)
        db.session.commit()
        db.session.delete(ride)
        db.session.commit()
        assert Ride.query.count() == 0


def test_ride_equipment_one_to_one(app):
    """
    Tests that the relationship between ride and equipment is one-to-one.
    i.e. that one ride cannot be ridden with more than one equipment.
    """

    ride = _get_ride()
    equipment_1 = _get_equipment(number=1)
    equipment_2 = _get_equipment(number=2)
    equipment_1.inRide = ride
    equipment_2.inRide = ride
    with app.app_context():
        db.session.add(ride)
        db.session.add(equipment_1)
        db.session.add(equipment_2)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_equipment_ondelete_user(app):
    """
    Tests that equipments's owner foreign key is set to null
    when the user is deleted.
    """

    equipment = _get_equipment()
    user = _get_user()
    equipment.ownedBy = user
    with app.app_context():
        db.session.add(equipment)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        assert equipment.owner is None


def test_component_ondelete_equipment(app):
    """
    Tests that components are deleted when parent equipment is deleted.
    """

    user = _get_user()
    equipment = _get_equipment()
    component = _get_component()
    component.owner = user
    component.installedTo = equipment
    with app.app_context():
        db.session.add(user)
        db.session.add(component)
        db.session.commit()
        db.session.delete(equipment)
        db.session.commit()
        assert Component.query.count() == 0


def test_user_columns(app):
    """
    Tests user columns' restrictions. Name must be unique and mandatory.
    """

    # Uniqueness of name
    user_1 = _get_user()
    user_2 = _get_user()
    with app.app_context():
        db.session.add(user_1)
        db.session.add(user_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null
    user = _get_user()
    with app.app_context():
        user.name = None
        db.session.add(user)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_equipment_columns(app):
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
    with app.app_context():
        db.session.add(equip_1)
        db.session.add(equip_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null name
    equipment = _get_equipment()
    equipment.name = None
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null category
    equipment = _get_equipment()
    equipment.category = None
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null brand
    equipment = _get_equipment()
    equipment.brand = None
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null model
    equipment = _get_equipment()
    equipment.model = None
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null date_added
    equipment = _get_equipment()
    equipment.date_added = None
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type int owner
    equipment = _get_equipment()
    equipment.owner = str(equipment.owner) + "kg"
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type datetime date_added
    equipment = _get_equipment()
    equipment.date_added = time.time()
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

    # Type datetime date_retired
    equipment = _get_equipment()
    equipment.date_retired = time.time()
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

    # date_retired greater than date_added
    equipment = _get_equipment()
    equipment.date_added = datetime.now()
    equipment.date_retired = datetime(2020, 1, 1, 0, 0, 0)
    with app.app_context():
        db.session.add(equipment)
        with pytest.raises(StatementError):
            db.session.commit()


def test_component_columns(app):
    """
    Tests component columns' restrictions. Category, brand, model and
    date_added must be mandatory. Date_added and date_retired must be type
    datetime and equipment_id accepts only numerical values.
    """

    # Uniqueness of category
    component_1 = _get_component()
    component_2 = _get_component()
    with app.app_context():
        db.session.add(component_1)
        db.session.add(component_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null category
    component = _get_component()
    component.name = None
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null category
    component = _get_component()
    component.category = None
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null brand
    component = _get_component()
    component.brand = None
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null model
    component = _get_component()
    component.model = None
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null date_added
    component = _get_component()
    component.date_added = None
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type int equipment_id
    component = _get_component()
    component.equipment_id = str(component.equipment_id) + "kg"
    with app.app_context():
        db.session.add(component)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type datetime date_added
    component = _get_component()
    component.date_added = time.time()
    with app.app_context():
        db.session.add(component)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

    # date_retired greater than date_added
    component = _get_component()
    component.date_added = datetime.now()
    component.date_retired = datetime(2020, 1, 1, 0, 0, 0)
    with app.app_context():
        db.session.add(component)
        with pytest.raises(StatementError):
            db.session.commit()


def test_ride_columns(app):
    """
    Tests that columns duration and datetime are mandatory.
    Tests that duration value only accepts integer values and that
    datetime only accepts datetime values.
    """

    # Uniqueness of name
    ride_1 = _get_ride()
    ride_2 = _get_ride()
    with app.app_context():
        db.session.add(ride_1)
        db.session.add(ride_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null name
    ride = _get_ride()
    ride.name = None
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null duration
    ride = _get_ride()
    ride.duration = None
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Not null datetime
    ride = _get_ride()
    ride.datetime = None
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type int duration
    ride = _get_ride()
    ride.duration = str(ride.duration) + "kg"
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # Type datetime
    ride = _get_ride()
    ride.datetime = time.time()
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

    # duration greater than zero
    ride = _get_ride()
    ride.duration = 0
    with app.app_context():
        db.session.add(ride)
        with pytest.raises(StatementError):
            db.session.commit()
