'''
Docstring to equipment resource routes
'''

# Library imports
from flask import request, Response, json, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

# Project imports
from cyequ import db
from cyequ.constants import MASON, EQUIPMENT_PROFILE, \
                            COMPONENT_PROFILE, LINK_RELATIONS_URL
from cyequ.utils import EquipmentBuilder, ComponentBuilder, \
                        create_error_response, check_for_json, \
                        validate_request_to_schema, check_db_existance
from cyequ.models import User, Equipment, Component  # , Ride
from cyequ.static.schemas.equipment_schema import equipment_schema
# from cyequ.static.schemas.ride_schema import ride_schema


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
            equip = EquipmentBuilder(name=equipment.name,
                                     category=equipment.category,
                                     date_added=equipment.date_added,
                                     date_retired=equipment.date_retired
                                     )
            # Add controls to each item
            equip.add_control("self", url_for("api.equipmentitem",
                                              user=user,
                                              equipment=equipment.name
                                              )
                              )
            equip.add_control("profile", EQUIPMENT_PROFILE)
            # Append each item to items-list of response body
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
        # Add equipment to db
        new_equip = Equipment(name=request.json["name"],
                              category=request.json["category"],
                              brand=request.json["brand"],
                              model=request.json["model"],
                              date_added=request.json["date_added"],
                              # Will look for date_retired and set as None,
                              # if not found
                              date_retired=request.json
                                           .get("date_retired", None),
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
                                         "Equipment with name '{}' already"
                                         " exists."
                                         .format(request.json["name"])
                                         )
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location":
                                 url_for("api.equipmentitem",
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
                                      Equipment.query
                                      .filter_by(name=equipment).first()
                                      )
        # Instantiate response message body
        body = EquipmentBuilder(name=db_equip.name,
                                category=db_equip.category,
                                brand=db_equip.brand,
                                model=db_equip.model,
                                date_added=db_equip.date_added,
                                date_retired=db_equip.date_retired,
                                user=db_user.name,
                                items=[]
                                )
        # Loop through all users in database and build each item with data and
        # controls.
        for component in db_equip.hasCompos:
            comp = ComponentBuilder(name=component.name,
                                    category=component.category,
                                    brand=component.brand,
                                    model=component.brand,
                                    date_added=component.date_added,
                                    date_retired=component.date_retired
                                    )
            # Add controls to each item
            comp.add_control("self", url_for("api.componentitem",
                                             user=user,
                                             equipment=equipment,
                                             component=component.name
                                             )
                             )
            comp.add_control("profile", COMPONENT_PROFILE)
            # Append each item to items-list of response body
            body["items"].append(comp)
        # Add controls response message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.equipmentitem",
                                         user=user,
                                         equipment=equipment
                                         )
                         )
        body.add_control("profile", EQUIPMENT_PROFILE)
        body.add_control("owner", url_for("equipmentbyuser", user=user))
        body.add_control_all_users()
        body.add_control_all_equipment(user)
        body.add_control_edit_equipment(user, equipment)
        body.add_control_delete_equipment(user, equipment)
        body.add_control_add_component(user, equipment)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user, equipment):
        '''
        POST-method definition for EquipmentItem resource. - Untested
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
        # Check if equipment is already retired
        if db_equip.date_retired is not None:
            return create_error_response(409,
                                         "Already retired",
                                         "Equipment of name '{}' is retired."
                                         " Cannot add component."
                                         .format(request.json["category"])
                                         )
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
        # Add a new component to db for equipment
        new_comp = Component(name=request.json["name"],
                             category=request.json["category"],
                             brand=request.json["brand"],
                             model=request.json["model"],
                             date_added=request.json["date_added"],
                             date_retired=request.json
                                          .get("date_retired", None),
                             equipment_id=db_equip.id
                             )
        try:
            db.session.add(new_comp)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409,
                                         "Already in service",
                                         "Unretired component of category"
                                         " '{}' already exists."
                                         .format(request.json["category"])
                                         )
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location":
                                 url_for("api.componentitem",
                                         user=user,
                                         equipment=equipment,
                                         component=request.json["category"]
                                         )
                                 }
                        )

    def put(self, user, equipment):
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
        # Update equipment data
        db_equip.name = request.json["name"]
        db_equip.category = request.json["category"]
        db_equip.brand = request.json["brand"]
        db_equip.model = request.json["model"]
        db_equip.date_added = request.json["date_added"]
        # When retiring equipment, also retire associated components
        # Check if date_retired given for equipment
        if request.json.get("date_retired", None) is not None:
            # Check if date_retired is later than date_added
            if db_equip.date_added >= request.json["date_retired"]:
                return create_error_response(409, "Inconsistent dates",
                                             "Retire date {} must be in the "
                                             "future with respect to"
                                             " added date {}"
                                             .format(request
                                                     .json["date_retired"],
                                                     db_equip.date_added)
                                             )
            # Update equipment date_retired
            db_equip.date_retired = request.json["date_retired"]
            # Loop all associated components for equipment
            for component in Component.query.filter_by(equipment_id=db_equip.id).all():  # noqa: 501
                # Update component date_retired
                component.date_retired = request.json["date_retired"]
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Equipment with name '{}' already "
                                         "exists.".format(request.json["name"])
                                         )
        return Response(status=204)

    def delete(self, user, equipment):
        '''
        DELETE-method definition for EquipmentItem resource. - Untested
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
        # Delete equipment
        try:
            db.session.delete(db_equip)
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
