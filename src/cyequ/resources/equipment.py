'''
Docstring to equipment resource routes
'''

# Library imports
from flask import request, Response, json, ulr_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from datetime import datetime

# Project imports
import cyequ.constants
from cyequ.utils import MasonBuilder, UserBuilder, \
                        EquipmentBuilder, ComponentBuilder, \
                        create_error_response, check_for_json, \
                        get_user_by_name, check_db_existance #, \
                        #RideBuilder
from cyequ.models import User, Equipment, Component #, Ride
from cyequ.static.schemas.user_schema import user_schema
from cyequ.static.schemas.equipment_schema import equipment_schema
from cyequ.static.schemas.component_schema import component_schema
#from cyequ.static.schemas.ride_schema import ride_schema


class EquipmentByUser(Resource):
    '''
    Class docstring here
    '''

    def get(self, user):
        '''
        GET-method definition for EquipmentByUser resource. - Untested
        '''

        # Find user by name in database. If not found, respond with error 404
        db_user = check_db_existance(user,
                                     User.query.filter_by(name=user).first()
                                     )
        # Instantiate message body
        body = EquipmentBuilder(items=[])
        # Add general controls to message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.equipmentbyuser"))
        body.add_control("cyequ-owner", url_for("api.useritem", user=user))
        body.add_control_add_equipment(user)
        # Loop through all equipment items owned by user
        for equipment in db_user.hasEquip:
            equip = EquipmentBuilder(
                name=equipment.name,
                category=equipment.category,
                date_added=equipment.date_added,
                date_retired=equipment.date_retired
            )
            # Add controls to each item
            equip.add_control("self", url_for("api.equipmentitem",
                                            user=user,
                                            equipment=equipment.name)
                                            )
            equip.add_control("profile", EQUIPMENT_PROFILE)
            # Add to message body
            body["items"].append(equip)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        '''
        POST-method definition for EquipmentByUser resource. - Untested
        '''
        # Check for json. If fails, respond with error 415
        check_for_json(request.json)
        # Validate request against the schema. If fails, respond with error 400
        validate_request_to_schema(request.json, equipment_schema())
        # Find user by name in database. If not found, respond with error 404
        db_user = check_db_existance(user,
                                     User.query.filter_by(name=user).first()
                                     )
        # Add equipment to db
        new_equip = Equipment(
            name=request.json["name"],
            category=request.json["category"],
            brand=request.json["brand"],
            model=request.json["model"],
            date_added=request.json["date_added"],
            date_retired=request.json["date_retired"],
            owner=db_user.id
        )
        try:
            db.session.add(new_equip)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409,
                                         "Already exists",
                                         "Equipment with name '{}' already" \
                                         " exists.".format(request.json["name"])
                                         )
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location": \
                                 url_for(api.equipmentitem,
                                         user=user,
                                         equipment=request.json["name"]
                                         )
                                 }
                        )


class EquipmentItem(Resource):
    '''
    Class docstring here
    '''

    def get(self, user, equipment):
        '''
        GET-method definition for EquipmentItem resource. - Untested
        '''

        # Find user by name in database. If not found, respond with error 404
        db_user = check_db_existance(user,
                                     User.query.filter_by(name=user).first()
                                     )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = check_db_existance(equipment,
                                     Equipment.query.filter_by(name=equipment).first()
                                     )
        # Instantiate response message body
        # Add ITEMS HERE!
        body = Equipment(
            name=request.json["name"],
            category=request.json["category"],
            brand=request.json["brand"],
            model=request.json["model"],
            date_added=request.json["date_added"],
            date_retired=request.json["date_retired"],
            user=user
        )
        # Add controls response message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.equipmentitem",
                                        user=user,
                                        equipment=equipment)
                                        )
        body.add_control("profile", EQUIPMENT_PROFILE)
        body.add_control("owner", url_for("equipmentbyuser", user=user))
        body.add_control_all_users()
        body.add_control_all_equipment(user)
        body.add_control_edit_equipment(user, equipment)
        body.add_control_delete_equipment(user, equipment)
        body.add_control_add_component(user, equipment)


        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, handle):
        # Check for json
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        # Validate request against the schema
        try:
            validate(request.json, Product.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))
        # Find product by handle in database. If not found, respond with error
        db_prod = Product.query.filter_by(handle=handle).first()
        if db_prod is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the given" \
                                         " handle {}".format(handle)
                                         )
        # Update product data
        db_prod.handle = request.json["handle"]
        db_prod.weight = request.json["weight"]
        db_prod.price = request.json["price"]
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Product with handle '{}' already " \
                                         "exists.".format(request.json["handle"])
                                         )
        return Response(status=204)

    def delete(self, handle):
        db_prod = Product.query.filter_by(handle=handle).first()
        if db_prod is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the " \
                                         "name {}".format(handle)
                                         )
        try:
            db.session.delete(db_prod)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(500, "Internal Server Error",
                                         "The server encountered an " \
                                         "unexpected condition that prevented" \
                                         " it from fulfilling the request."
                                         )
        return Response(status=204)
