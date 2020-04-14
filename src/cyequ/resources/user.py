'''
Docstring to user resource routes
'''

# Library imports
from flask import request, Response, json, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
# from werkzeug.exceptions import BadRequest

# Project imports
from cyequ import db
from cyequ.constants import MASON, USER_PROFILE, LINK_RELATIONS_URL
from cyequ.utils import UserBuilder, \
                        create_error_response, check_for_json, \
                        validate_request_to_schema, check_db_existance
from cyequ.models import User
from cyequ.static.schemas.user_schema import user_schema


class UserCollection(Resource):
    '''
    Class docstring here
    '''

    def get(self):
        '''
        GET-method definition for UserCollection resource. - Untested
        '''

        # Instantiate message body
        body = UserBuilder(items=[])
        # Add general controls to message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.usercollection"))
        body.add_control_add_user()
        # Loop through all users in database and build each item with data and
        # controls.
        for db_user in User.query.all():
            usr = UserBuilder(
                name=db_user.name
            )
            # Add controls to each item
            usr.add_control("self", url_for("api.useritem", user=db_user.name))
            usr.add_control("profile", USER_PROFILE)
            # Append each item to items-list of response body
            body["items"].append(usr)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        '''
        POST-method definition for UserCollection resource. - Untested
        '''

        # Check for json. If fails, respond with error 415
        check_for_json(request.json)
        # Validate request against the schema. If fails, respond with error 400
        validate_request_to_schema(request.json, user_schema())
        # Add user to db
        user = User(
            name=request.json["name"]
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409,
                                         "Already exists",
                                         "User with name '{}' already"
                                         " exists."
                                         .format(request.json["user"])
                                         )
        # Respond with location of new resource
        return Response(status=201,
                        headers={"Location":
                                 url_for("api.useritem", user=user.name)
                                 }
                        )


class UserItem(Resource):
    '''
    Class docstring here
    '''

    def get(self, user):
        '''
        GET-method definition for UserItem resource. - Untested
        '''

        # Find user by name in database. If not found, respond with error 404
        db_user = check_db_existance(user,
                                     User.query.filter_by(name=user).first()
                                     )
        # Instantiate response message body
        body = UserBuilder(
            user=db_user.name
        )
        # Add controls to message body
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.useritem", user=user))
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", url_for("api.usercollection"))
        body.add_control_edit_user(user)
        body.add_control_all_equipment(user)
        return Response(json.dumps(body), 200, mimetype=MASON)

    # Not implemented
    def put(self, user):
        '''
        PUT-method definition for UserItem resource. - Untested

        '''

        # Check for json. If fails, respond with error 415
        check_for_json(request.json)
        # Validate request against the schema. If fails, respond with error 400
        validate_request_to_schema(request.json, user_schema())
        # Find user by name in database. If not found, respond with error 404
        db_user = check_db_existance(user,
                                     User.query.filter_by(name=user).first()
                                     )
        # Update user data
        db_user.name = request.json["name"]
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "User with name '{}' already "
                                         "exists.".format(request.json["name"])
                                         )
        return Response(status=204)

#    def delete(self, user):
#        '''
#        DELETE-method definition for UserItem resource. - Untested
#        Not Implemented
#        '''
#
#        # Find user by name in database. If not found, respond with error 404
#        db_user = check_db_existance(user,
#                                     User.query.filter_by(name=user).first()
#                                     )
#         # Delete user
#        try:
#            db.session.delete(db_user)
#            db.session.commit()
#        except IntegrityError:
#            # In case of database error
#            db.session.rollback()
#            return create_error_response(500, "Internal Server Error",
#                                         "The server encountered an "
#                                         "unexpected condition that prevented"
#                                         " it from fulfilling the request."
#                                         )
#        return Response(status=204)
