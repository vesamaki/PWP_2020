"""
This module includes the functionality of
    Cyclist equipment usage API.
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
from flask import request, abort, json, Blueprint, ulr_for, redirect
#from sqlalchemy.engine import Engine
from werkzeug.exceptions import BadRequest
from datetime import datetime
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import event
from flask_restful import Resource, Api

# Project imports
import cyequ.constants

api_bp = Blueprint("api", __name__)
ref_bp = Blueprint("reference", __name__)
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from cyequ.resources.user import UserCollection, UserItem
from cyequ.resources.equipment import EquipmentByUser, EquipmentItem
from cyequ.resources.component import ComponentItem





# API Entry Point - Untested
@api_bp.route("/")
def entry_point():
    body = CyequBuilder()
    body.add_namespace("cyequ", LINK_RELATIONS_URL)
    body.add_control_all_users()
    return Response(json.dumps(body), 200, mimetype="MASON")

# Adapted from PWP Ex3
# Static route: Link relations - Untested
@app.route(LINK_RELATIONS_URL)
def redirect_to_apiary_link_rels():
    return redirect(APIARY_URL + "link-relations")

# Static route: User Profile - Untested
@app.route(USER_PROFILE)
def redirect_to_apiary_user_prof():
    return redirect(APIARY_URL + "user-profile")

# Static route: Equipment Profile - Untested
@app.route(EQUIPMENT_PROFILE)
def redirect_to_apiary_equip_prof():
    return redirect(APIARY_URL + "equipment-profile")

# Static route: Component Profile - Untested
@app.route(COMPONENT_PROFILE)
def redirect_to_apiary_comp_prof():
    return redirect(APIARY_URL + "component-profile")

# Static route: Error Profile - Untested
@app.route(ERROR_PROFILE)
def redirect_to_apiary_err_prof():
    return redirect(APIARY_URL + "error-profile")

# Registering resource routes - Untested
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<user>/")
api.add_resource(EquipmentByUser, "/api/users/<user>/all_equipment/")
api.add_resource(EquipmentItem, "/api/users/<user>//all_equipment/<equipment>/")
api.add_resource(ComponentItem, "/api/users/<user>//all_equipment/<equipment>/<component>")
