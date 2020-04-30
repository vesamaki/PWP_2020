"""
This module includes the functionality of
    Cyclist equipment usage API.
Run with:
    flask run
See https://github.com/vesamaki/PWP_2020 for details
"""

# Library imports
from flask import Blueprint, redirect
from flask_restful import Api

# Project imports
from cyequ.constants import USER_PROFILE, EQUIPMENT_PROFILE, \
                            COMPONENT_PROFILE, ERROR_PROFILE, \
                            LINK_RELATIONS_URL, APIARY_URL

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from cyequ.resources.entry import Entry  # noqa:E402
from cyequ.resources.user import UserCollection, UserItem  # noqa:E402
from cyequ.resources.equipment import EquipmentByUser, \
                                      EquipmentItem  # noqa:E402
from cyequ.resources.component import ComponentItem  # noqa:E402

# Adapted from PWP Ex3
# Static route: Link relations
@api_bp.route(LINK_RELATIONS_URL, methods=['GET'])
def redirect_to_apiary_link_rels():
    '''
    Redirect to API's APIARY-documentation for link relations url.
    '''
    return redirect(APIARY_URL + "link-relations")

# Static route: User Profile
@api_bp.route(USER_PROFILE, methods=['GET'])
def redirect_to_apiary_user_prof():
    '''
    Redirect to API's APIARY-documentation for user profile url.
    '''
    return redirect(APIARY_URL + "user-profile")

# Static route: Equipment Profile
@api_bp.route(EQUIPMENT_PROFILE, methods=['GET'])
def redirect_to_apiary_equip_prof():
    '''
    Redirect to API's APIARY-documentation for equipment profile url.
    '''
    return redirect(APIARY_URL + "equipment-profile")

# Static route: Component Profile
@api_bp.route(COMPONENT_PROFILE, methods=['GET'])
def redirect_to_apiary_comp_prof():
    '''
    Redirect to API's APIARY-documentation for component profile url.
    '''
    return redirect(APIARY_URL + "component-profile")

# Static route: Error Profile
@api_bp.route(ERROR_PROFILE, methods=['GET'])
def redirect_to_apiary_err_prof():
    '''
    Redirect to API's APIARY-documentation for error profile url.
    '''
    return redirect(APIARY_URL + "error-profile")


# Registering resource routes
api.add_resource(Entry, "/api/")
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<user>/")
api.add_resource(EquipmentByUser, "/api/users/<user>/all_equipment/")
api.add_resource(EquipmentItem, "/api/users/<user>/all_equipment/<equipment>/")
api.add_resource(ComponentItem, "/api/users/<user>/all_equipment/"
                                "<equipment>/<component>/")
