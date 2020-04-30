'''
This module holds class-definitions for the API entry point resource.
'''

# Library imports
from flask import Response, json
from flask_restful import Resource

# Project imports
from cyequ.constants import LINK_RELATIONS_URL, MASON
from cyequ.utils import UserBuilder


# API Entry URL - Untested
class Entry(Resource):
    '''
    This resource is used as an entry point to the API
    '''

    def get(self):
        '''
        Builds the response body and adds link relation cyequ:users-all as the
        sole control.
        '''

        body = UserBuilder()
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control_all_users()
        return Response(json.dumps(body), 200, mimetype=MASON)
