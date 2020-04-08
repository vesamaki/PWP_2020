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
from flask import request, abort, json, Blueprint, ulr_for, #Flask 
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
from cyequ.resources.equipment import UserCollection, UserItem
from cyequ.resources.component import UserCollection, UserItem


# Constants
MASON = "application/vnd.mason+json"
PRODUCT_PROFILE = "/profiles/product/"
ERROR_PROFILE = "/profiles/error/"
LINK_RELATIONS_URL = "/storage/link-relations/"
APIARY_URL = "https://yourproject.docs.apiary.io/#reference/"


# API Entry Point
@api_bp.route("/")
def entry_point():
    body = InventoryBuilder()
    body.add_namespace("storage", LINK_RELATIONS_URL)
    body.add_control_all_products()
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

api.add_resource(ProductCollection, "/api/products/")
api.add_resource(ProductItem, "/api/products/<handle>/")