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
    In unit tests you need to take care to
    use the with app.app_context() statement.
"""

# Library imports
from flask import Blueprint, redirect
from flask_restful import Api

# Project imports
from cyequ.constants import USER_PROFILE, EQUIPMENT_PROFILE, \
                            COMPONENT_PROFILE, ERROR_PROFILE, \
                            LINK_RELATIONS_URL, APIARY_URL

api_bp = Blueprint("api", __name__)
# ref_bp = Blueprint("reference", __name__)  # , url_prefix="")
api = Api(api_bp)

# this import must be placed after we create api to avoid issues with
# circular imports
from cyequ.resources.entry import Entry  # noqa:E402
from cyequ.resources.user import UserCollection, UserItem  # noqa:E402
from cyequ.resources.equipment import EquipmentByUser, \
                                      EquipmentItem  # noqa:E402
from cyequ.resources.component import ComponentItem  # noqa:E402

# Adapted from PWP Ex3
# Static route: Link relations - DONE
@api_bp.route(LINK_RELATIONS_URL, methods=['GET'])
def redirect_to_apiary_link_rels():
    return redirect(APIARY_URL + "link-relations")

# Static route: User Profile - DONE
@api_bp.route(USER_PROFILE, methods=['GET'])
def redirect_to_apiary_user_prof():
    return redirect(APIARY_URL + "user-profile")

# Static route: Equipment Profile - DONE
@api_bp.route(EQUIPMENT_PROFILE, methods=['GET'])
def redirect_to_apiary_equip_prof():
    return redirect(APIARY_URL + "equipment-profile")

# Static route: Component Profile - DONE
@api_bp.route(COMPONENT_PROFILE, methods=['GET'])
def redirect_to_apiary_comp_prof():
    return redirect(APIARY_URL + "component-profile")

# Static route: Error Profile - DONE
@api_bp.route(ERROR_PROFILE, methods=['GET'])
def redirect_to_apiary_err_prof():
    return redirect(APIARY_URL + "error-profile")


# Registering resource routes - DONE
api.add_resource(Entry, "/api/")  # DONE
api.add_resource(UserCollection, "/api/users/")  # DONE
api.add_resource(UserItem, "/api/users/<user>/")
api.add_resource(EquipmentByUser, "/api/users/<user>/all_equipment/")
api.add_resource(EquipmentItem, "/api/users/<user>/all_equipment/<equipment>/")
api.add_resource(ComponentItem, "/api/users/<user>/all_equipment/"
                                "<equipment>/<component>/")
