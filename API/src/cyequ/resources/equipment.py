'''
This module holds class-definitions for the API equipment resources.
'''

# Library imports
from flask import request, Response, json, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from datetime import datetime

# Project imports
from cyequ import db
from cyequ.constants import MASON, EQUIPMENT_PROFILE, \
                            COMPONENT_PROFILE, LINK_RELATIONS_URL
from cyequ.utils import EquipmentBuilder, ComponentBuilder, \
                        create_error_response, convert_req_date
from cyequ.models import User, Equipment, Component  # , Ride
from cyequ.static.schemas.equipment_schema import equipment_schema
from cyequ.static.schemas.component_schema import component_schema
# from cyequ.static.schemas.ride_schema import ride_schema


class EquipmentByUser(Resource):
    '''
    This class defines responses for EquipmentByUser resource.
    '''

    def get(self, user):
        '''
        GET-method definition.
        Builds the response body and adds controls as defined in API design

        Returns flask Response object.
        '''

        # Find user by name in database. If not found, respond with error 404
        db_user = User.query.filter_by(uri=user).first()
        if db_user is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Instantiate message body
        body = EquipmentBuilder(items=[])
        # Add general controls to message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self",
                         url_for("api.equipmentbyuser", user=user),
                         title="Get a list of all equipment owned by "
                               "the given user."
                         )
        body.add_control("cyequ:owner",
                         url_for("api.useritem", user=user),
                         title="Get associated user's information."
                         )
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
                                              equipment=equipment.uri
                                              ),
                              title="Get this equipment's information."
                              )
            equip.add_control("profile",
                              EQUIPMENT_PROFILE,
                              title="Get the profile of equipment resource."
                              )
            # Append each item to items-list of response body
            body["items"].append(equip)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        '''
        POST-method definition.
        Checks for appropriate request body and creates a new equipment
        resource in the API.

        Exceptions.
        jsonschema.ValidationError. If request is not
            a valid JSON document.
        sqlalchemy.exc.IntegrityError. Violation of SQLite database
            integrity.

        Returns flask Response object.
        '''

        # Check for json. If fails, respond with error 415
        if request.json is None:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        # Validate request against the schema. If fails, respond with error 400
        try:
            validate(request.json, component_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON"
                                         "document", str(err)
                                         )
        # Find user by name in database. If not found, respond with error 404
        db_user = User.query.filter_by(uri=user).first()
        if db_user is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Convert %Y-%m-%d %H:%M:%S dates to Python datetime format
        p_date_added = convert_req_date(request.json.get("date_added"))
        p_date_retired = convert_req_date(request.json.get("date_retired"))
        # Check if date_retired given
        if p_date_retired is not None:
            # Check if date_retired is later than date_added
            if p_date_added >= p_date_retired:
                return create_error_response(409, "Inconsistent dates",
                                             "Retire date {} must be in the "
                                             "future with respect to"
                                             " added date {}"
                                             .format(p_date_retired,
                                                     p_date_added
                                                     )
                                             )
        # Add equipment to db
        new_equip = Equipment(name=request.json["name"],
                              category=request.json["category"],
                              brand=request.json["brand"],
                              model=request.json["model"],
                              date_added=p_date_added,
                              date_retired=p_date_retired,
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
                                         " exists for this user."
                                         .format(request.json["name"])
                                         )
        # Find new equipment by name in database.
        db_equip = Equipment.query.filter_by(name=request.json["name"]).first()
        # Create URI for user
        db_equip.uri = db_equip.name + str(db_equip.id)
        db.session.commit()
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location":
                                 url_for("api.equipmentitem",
                                         user=user,
                                         equipment=db_equip.uri
                                         )
                                 }
                        )


class EquipmentItem(Resource):
    '''
    This class defines responses for EquipmentItem resource.
    '''

    def get(self, user, equipment):
        '''
        GET-method definition.
        Builds the response body and adds controls as defined in API design

        Returns flask Response object.
        '''

        # Find user by name in database. If not found, respond with error 404
        db_user = User.query.filter_by(uri=user).first()
        if db_user is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = Equipment.query.filter_by(uri=equipment).first()
        if db_equip is None:
            return create_error_response(404, "Not found",
                                         "No equipment was found with URI {}"
                                         .format(equipment)
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
            # If component is in active service, don't attach retired_date
            if component.date_retired == datetime(9999, 12, 31, 23, 59, 59):
                comp = ComponentBuilder(name=component.name,
                                        category=component.category,
                                        brand=component.brand,
                                        model=component.brand,
                                        date_added=component.date_added
                                        )
            else:
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
                                             component=component.uri
                                             ),
                             title="Get this component's information."
                             )
            comp.add_control("profile",
                             COMPONENT_PROFILE,
                             title="Get profile of component resource."
                             )
            # Append each item to items-list of response body
            body["items"].append(comp)
        # Add controls response message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.equipmentitem",
                                         user=user,
                                         equipment=equipment
                                         ),
                         title="Get this equipment's information."
                         )
        body.add_control("profile",
                         EQUIPMENT_PROFILE,
                         title="Get profile of equipment resource."
                         )
        body.add_control("cyequ:owner",
                         url_for("api.equipmentbyuser", user=user),
                         title="Get associated user's information."
                         )
        body.add_control_all_users()
        body.add_control_all_equipment(user)
        body.add_control_edit_equipment(user, equipment)
        body.add_control_delete_equipment(user, equipment)
        body.add_control_add_component(user, equipment)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user, equipment):
        '''
        POST-method definition.
        Checks for appropriate request body and creates a new component
        resource in the API.

        Exceptions.
        jsonschema.ValidationError. If request is not
            a valid JSON document.
        sqlalchemy.exc.IntegrityError. Violation of SQLite database
            integrity.

        Returns flask Response object.
        '''

        # Check for json. If fails, respond with error 415
        if request.json is None:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        # Validate request against the schema. If fails, respond with error 400
        try:
            validate(request.json, equipment_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON "
                                         "document", str(err)
                                         )
        # Find user by name in database. If not found, respond with error 404
        if User.query.filter_by(uri=user).first() is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = Equipment.query.filter_by(uri=equipment).first()
        if db_equip is None:
            return create_error_response(404, "Not found",
                                         "No equipment was found with URI {}"
                                         .format(equipment)
                                         )
        # Check if equipment is already retired
        if db_equip.date_retired is not None:
            return create_error_response(409,
                                         "Already retired",
                                         "Equipment of URI '{}' is retired."
                                         " Cannot add component {}."
                                         .format(db_equip.uri,
                                                 request.json["category"]
                                                 )
                                         )
        # Date checks
        # Convert %Y-%m-%d %H:%M:%S dates to Python datetime format
        p_date_added = convert_req_date(request.json.get("date_added"))
        # Check that component date added is not before
        # associated equipment's date added
        if p_date_added < db_equip.date_added:
            return create_error_response(409, "Inconsistent dates",
                                         "Components's date added {} must be"
                                         " after associated equipment's "
                                         "date added {}"
                                         .format(db_equip.date_added,
                                                 p_date_added
                                                 )
                                         )
        # Check if date_retired given and convert
        p_date_retired = convert_req_date(request.json.get("date_retired"))
        if p_date_retired is not None:
            if p_date_added >= p_date_retired:
                return create_error_response(409, "Inconsistent dates",
                                             "Retire date {} must be in the "
                                             "future with respect to"
                                             " added date {}"
                                             .format(p_date_retired,
                                                     p_date_added
                                                     )
                                             )
        else:
            # If not given, set to faaar in the future.
            # Meaning component is currently installed to equipment
            p_date_retired = convert_req_date("9999-12-31 23:59:59")
        # Add a new component to db for equipment
        new_comp = Component(name=request.json["name"],
                             category=request.json["category"],
                             brand=request.json["brand"],
                             model=request.json["model"],
                             date_added=p_date_added,
                             date_retired=p_date_retired,
                             equipment_id=db_equip.id
                             )
        try:
            db.session.add(new_comp)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            # Currently doesn't work.
            # No functioning constraint for unique "active component".
            return create_error_response(409,
                                         "Already in service",
                                         "Unretired component of category"
                                         " '{}' already exists."
                                         .format(request.json["category"])
                                         )
        # Find new component by category & date_retired in database.
        db_comp = Component.query.filter_by(category=request.json["category"],
                                            date_retired=p_date_retired
                                            ).first()
        # Create URI for user
        db_comp.uri = db_comp.name + str(db_comp.id)
        db.session.commit()
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location":
                                 url_for("api.componentitem",
                                         user=user,
                                         equipment=equipment,
                                         component=db_comp.uri
                                         )
                                 }
                        )

    def put(self, user, equipment):
        '''
        PUT-method definition.
        Checks for appropriate request body and modifies an equipment resource
        in the API.

        Exceptions.
        jsonschema.ValidationError. If request is not
            a valid JSON document.
        sqlalchemy.exc.IntegrityError. Violation of SQLite database
            integrity.

        Returns flask Response object.
        '''

        # Check for json. If fails, respond with error 415
        if request.json is None:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        # Validate request against the schema. If fails, respond with error 400
        try:
            validate(request.json, equipment_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON "
                                         "document", str(err)
                                         )
        # Find user by name in database. If not found, respond with error 404
        if User.query.filter_by(uri=user).first() is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = Equipment.query.filter_by(uri=equipment).first()
        if db_equip is None:
            return create_error_response(404, "Not found",
                                         "No equipment was found with URI {}"
                                         .format(equipment)
                                         )
        # Convert %Y-%m-%d %H:%M:%S dates to Python datetime format
        p_date_added = convert_req_date(request.json.get("date_added"))
        p_date_retired = convert_req_date(request.json.get("date_retired"))
        # Update equipment data
        db_equip.name = request.json["name"]
        db_equip.category = request.json["category"]
        db_equip.brand = request.json["brand"]
        db_equip.model = request.json["model"]
        # Make sure equipment date_added cannot be moved forward in time if
        # equipment has associated components
        if db_equip.date_added >= p_date_added:
            db_equip.date_added = p_date_added
        elif not Component.query.filter_by(equipment_id=db_equip.id).first():
            db_equip.date_added = p_date_added
        else:
            return create_error_response(409, "Inconsistent dates",
                                         "New added date {} must not be in the"
                                         "future of current added date {} if "
                                         "equipment has components associated"
                                         " with it"
                                         .format(p_date_added,
                                                 db_equip.date_added
                                                 )
                                         )
        # When retiring equipment, also retire associated components
        # Check if date_retired given for equipment
        if request.json.get("date_retired") is not None:
            # Check if date_retired is later than date_added
            if p_date_added >= p_date_retired:
                return create_error_response(409, "Inconsistent dates",
                                             "Retire date {} must be in the "
                                             "future with respect to"
                                             " added date {}"
                                             .format(p_date_retired,
                                                     p_date_added
                                                     )
                                             )
            # Update equipment date_retired
            db_equip.date_retired = p_date_retired
            # Loop all associated components for equipment
            for component in Component.query.filter_by(equipment_id=db_equip.id).all():  # noqa: 501
                # Update component date_retired
                component.date_retired = p_date_retired
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Equipment with name '{}' already "
                                         "exists for user."
                                         .format(request.json["name"])
                                         )
        return Response(status=204)

    def delete(self, user, equipment):
        '''
        DELETE-method definition.
        Deletes an equipment resource in the API.

        Returns flask Response object.
        '''

        # Find user by name in database. If not found, respond with error 404
        if User.query.filter_by(uri=user).first() is None:
            return create_error_response(404, "Not found",
                                         "No user was found with URI {}"
                                         .format(user)
                                         )
        # Find equipment by name in database.
        # If not found, respond with error 404
        db_equip = Equipment.query.filter_by(uri=equipment).first()
        if db_equip is None:
            return create_error_response(404, "Not found",
                                         "No equipment was found with URI {}"
                                         .format(equipment)
                                         )
        # Delete equipment
        db.session.delete(db_equip)
        db.session.commit()
        return Response(status=204)
