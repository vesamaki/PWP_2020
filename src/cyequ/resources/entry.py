'''
This is the entry URL for the API
'''

# Library imports
from flask import Response, json
from flask_restful import Resource

# Project imports
from cyequ.constants import LINK_RELATIONS_URL, MASON
from cyequ.utils import UserBuilder


# API Entry URL - Untested
class EntryURL(Resource):
    '''
    Class docstring here
    '''

    def get(self):
        body = UserBuilder()
        body.add_namespace("cyequ", LINK_RELATIONS_URL)
        body.add_control_all_users()
        print(json.dumps(body))
        return Response(json.dumps(body), 200, mimetype=MASON)
