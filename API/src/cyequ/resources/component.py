'''
This module holds class-definitions for the API component resources.
'''

# Library imports
from flask import request, Response, json, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError

# Project imports
from cyequ import db
from cyequ.constants import MASON, COMPONENT_PROFILE, LINK_RELATIONS_URL
from cyequ.utils import ComponentBuilder, create_error_response, \
                        convert_req_date
from cyequ.models import User, Equipment, Component  # , Ride
from cyequ.static.schemas.component_schema import component_schema
# from cyequ.static.schemas.ride_schema import ride_schema


class ComponentItem(Resource):
    '''
    This class defines responses for ComponentItem resource.
    '''

    def get(self, user, equipment, component):
        '''
        GET-method definition.
        Builds the response body and adds controls as defined in API design

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
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = Component.query.filter_by(uri=component).first()
        if db_comp is None:
            return create_error_response(404, "Not found",
                                         "No component was found with "
                                         "URI {}"
                                         .format(component)
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
        body.add_control("self",
                         url_for("api.componentitem",
                                 user=user,
                                 equipment=equipment,
                                 component=component
                                 ),
                         title="Get this component's information."
                         )
        body.add_control("profile",
                         COMPONENT_PROFILE,
                         title="Get profile of component resource."
                         )
        body.add_control("up", url_for("api.equipmentitem",
                                       user=user,
                                       equipment=equipment
                                       ),
                         title="Get associated equipment's information."
                         )
        body.add_control_all_users()
        body.add_control_edit_component(user, equipment, component)
        body.add_control_delete_component(user, equipment, component)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user, equipment, component):
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
            validate(request.json, component_schema())
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
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = Component.query.filter_by(uri=component).first()
        if db_comp is None:
            return create_error_response(404, "Not found",
                                         "No component was found with "
                                         "URI {}"
                                         .format(component)
                                         )
        # Convert %Y-%m-%d %H:%M:%S dates to Python datetime format
        p_date_added = convert_req_date(request.json.get("date_added"))
        p_date_retired = convert_req_date(request.json.get("date_retired"))
        # Update equipment data
        db_comp.name = request.json["name"]
        db_comp.category = request.json["category"]
        db_comp.brand = request.json["brand"]
        db_comp.model = request.json["model"]
        # Make sure component date_added cannot be moved backward in time
        # past associated equipment's date_added
        if db_equip.date_added <= p_date_added:
            db_comp.date_added = p_date_added
        else:
            return create_error_response(409, "Inconsistent dates",
                                         "New added date {} must be at or in "
                                         "the future of associated equipment's"
                                         " current added date {}"
                                         .format(p_date_added,
                                                 db_equip.date_added
                                                 )
                                         )
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
            # Check if equipment is already retired
            # Components are retired, when equipment is retired
            # Cannot re- or unretire components of retired equipment
            elif db_equip.date_retired is not None:
                return create_error_response(409, "Not allowed",
                                             "Cannot reretire components of a"
                                             " retired equipment {}"
                                             .format(db_equip.uri)
                                             )
            else:
                db_comp.date_retired = p_date_retired
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Unretired component of category"
                                         " {} already exists."
                                         .format(request.json["category"])
                                         )
        return Response(status=204)

    def delete(self, user, equipment, component):
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
        if Equipment.query.filter_by(uri=equipment).first() is None:
            return create_error_response(404, "Not found",
                                         "No equipment was found with URI {}"
                                         .format(equipment)
                                         )
        # Find component by category in database.
        # If not found, respond with error 404
        db_comp = Component.query.filter_by(uri=component).first()
        if db_comp is None:
            return create_error_response(404, "Not found",
                                         "No component was found with "
                                         "URI {}"
                                         .format(component)
                                         )
        # Delete equipment
        db.session.delete(db_comp)
        db.session.commit()
        return Response(status=204)
