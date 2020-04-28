'''
This module defines the User json schema of Cycling Equipment Usage API

'''


def user_schema():
    '''
    Defines the user schema
    '''

    schema = {
        "title": "User schema",
        "type": "object",
        "required": ["name"]
    }
    props = schema["properties"] = {}
    props["name"] = {
        "description": "The user's name",
        "type": "string",
        "minLength": 2,
        "maxLength": 64
    }
    return schema
