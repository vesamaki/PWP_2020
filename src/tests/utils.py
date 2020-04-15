"""
This module is used to test my PWP database of app.py.
Run with:
    pytest db_tests.py
or with additional details:
    pytest db_tests.py --cov --pep8
"""

# Library imports
from datetime import datetime

# Project imports
from cyequ.models import User, Equipment, Component, Ride


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
