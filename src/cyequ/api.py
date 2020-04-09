"""
This module includes the functionality of
    Cycling equipment usage API.
Run with:
    flask run
See https://github.com/vesamaki/PWP_2020 for details


NOTES:
api.ulr_for -> ulr_for:
    href = url_for("api.sensoritem", sensor="uo-donkeysensor-1")
    Resources defined here in api.
    In unit tests you need to take care to use the with app.app_context() statement.
"""

# Library imports
from flask import request, abort, json, Blueprint, ulr_for, redirect #Flask
from sqlalchemy.exc import IntegrityError
#from sqlalchemy.engine import Engine
from werkzeug.exceptions import BadRequest
from datetime import datetime
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import event
from flask_restful import Resource, Api

# Project module imports
from .models import User, Equipment, Component #, Ride
from .schema import user_schema, equipment_schema, component_schema, #ride_schema

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from cyequ.resources.user import UserCollection, UserItem
from cyequ.resources.equipment import EquipmentByUser, EquipmentItem
from cyequ.resources.component import ComponentItem


# Constants
MASON = "application/vnd.mason+json"
USER_PROFILE = "/cyequ/profiles/user/"
ERROR_PROFILE = "/cyequ/profiles/error/"
LINK_RELATIONS_URL = "/cyequ/link-relations/"
APIARY_URL = "https://cyclistequipmentusageapipwpcourse.docs.apiary.io/#reference/"


# API Entry Point
@api_bp.route("/")
def entry_point():
    body = CyequBuilder()
    body.add_namespace("cyequ", LINK_RELATIONS_URL)
    body.add_control_all_users()
    return Response(json.dumps(body), 200, mimetype="MASON")

@app.route(LINK_RELATIONS_URL)
def to_link_rels():
    return Response(LINK_RELATIONS_URL, 200, mimetype="text/html")

@app.route(PRODUCT_PROFILE)
def to_prod_profiles():
    return Response(PRODUCT_PROFILE, 200, mimetype="text/html")

@app.route(ERROR_PROFILE)
def to_err_profiles():
    return Response(ERROR_PROFILE, 200, mimetype="text/html")

# Registering resource routes - DONE
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<user>/")
api.add_resource(EquipmentByUser, "/api/users/<user>/all_equipment/")
api.add_resource(EquipmentItem, "/api/users/<user>//all_equipment/<equipment>/")
api.add_resource(ComponentItem, "/api/users/<user>//all_equipment/<equipment>/<component>")
