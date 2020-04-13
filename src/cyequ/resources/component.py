'''
Docstring to component resource routes
'''

# Library imports
from flask import request, Response, json, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

# Project imports
from cyequ import db
from cyequ.constants import MASON, COMPONENT_PROFILE, LINK_RELATIONS_URL
from cyequ.utils import ComponentBuilder, \
                        create_error_response, check_for_json, \
                        validate_request_to_schema, check_db_existance
from cyequ.models import User, Equipment, Component  # , Ride
from cyequ.static.schemas.equipment_schema import equipment_schema
# from cyequ.static.schemas.ride_schema import ride_schema


class ComponentItem(Resource):
    '''
    Class docstring here
    '''

    def get(self, user, equipment, component):
        '''
        GET-method definition for ComponentItem resource. - Untested
        '''

        # Find user by name in database. If not found, respond with error 404
        check_db_existance(user,
                           User.query.filter_by(name=user).first()
                           )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = check_db_existance(equipment,
                                      Equipment.query
                                      .filter_by(name=equipment).first()
                                      )
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = check_db_existance(component,
                                     Component.query
                                     .filter_by(category=component).first()
                                     )
        # Instantiate response message body and include component data
        body = ComponentBuilder(name=db_comp.name,
                                category=db_comp.category,
                                brand=db_comp.brand,
                                model=db_comp.model,
                                date_added=db_comp.date_added,
                                date_retired=db_comp.date_retired,
                                equipment=db_equip.name
                                )
        # Add controls to message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.componentitem",
                                         user=user,
                                         equipment=equipment,
                                         component=component
                                         )
                         )
        body.add_control("profile", COMPONENT_PROFILE)
        body.add_control("up", url_for("api.equipmentitem",
                                       user=user,
                                       equipment=equipment
                                       )
                         )
        body.add_control_all_users()
        body.add_control_edit_component(user, equipment, component)
        body.add_control_delete_component(user, equipment, component)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user, equipment, component):
        '''
        PUT-method definition for EquipmentItem resource. - Untested
        '''

        # Check for json. If fails, respond with error 415
        check_for_json(request.json)
        # Validate request against the schema. If fails, respond with error 400
        validate_request_to_schema(request.json, equipment_schema())
        # Find user by name in database. If not found, respond with error 404
        check_db_existance(user,
                           User.query.filter_by(name=user).first()
                           )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = check_db_existance(equipment,
                                      Equipment.query
                                      .filter_by(name=equipment).first()
                                      )
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = check_db_existance(component,
                                     Component.query
                                     .filter_by(category=component).first()
                                     )
        # Update equipment data
        db_comp.name = request.json["name"]
        db_comp.category = request.json["category"]
        db_comp.brand = request.json["brand"]
        db_comp.model = request.json["model"]
        db_comp.date_added = request.json["date_added"]
        # Check if date_retired given
        if request.json.get("date_retired", None) is not None:
            # Check if date_retired is later than date_added
            if request.json["date_added"] >= request.json["date_retired"]:
                return create_error_response(409, "Inconsistent dates",
                                             "Retire date {} must be in the "
                                             "future with respect to"
                                             " added date {}"
                                             .format(request
                                                     .json["date_retired"],
                                                     request
                                                     .json["date_added"])
                                             )
            # Check if equipment is already retired
            # Components are retired, when equipment is retired
            # Cannot re- or unretire components of retired equipment
            if db_equip.date_retired is None:
                db_comp.date_retired = request.json["date_retired"]
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Component of category '{}' already "
                                         "exists."
                                         .format(request.json["category"])
                                         )
        return Response(status=204)

    def delete(self, user, equipment, component):
        '''
        DELETE-method definition for ComponentItem resource. - Untested
        '''

        # Find user by name in database. If not found, respond with error 404
        check_db_existance(user,
                           User.query.filter_by(name=user).first()
                           )
        # Find equipment by name in database.
        # If not found, respond with error 404
        check_db_existance(equipment,
                           Equipment.query.filter_by(name=equipment).first()
                           )
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = check_db_existance(component,
                                     Component.query
                                     .filter_by(category=component).first()
                                     )
        # Delete equipment
        try:
            db.session.delete(db_comp)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(500, "Internal Server Error",
                                         "The server encountered an "
                                         "unexpected condition that prevented"
                                         " it from fulfilling the request."
                                         )
        return Response(status=204)
