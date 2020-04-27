'''
This module defines the Ride json schema for Cycling Equipment Usage API

'''


def ride_schema():
    '''
    Defines the ride schema
    '''

    schema = {
        "type": "object",
        "required": ["name", "duration", "datetime"]
    }
    props = schema["properties"] = {}
    props["name"] = {
        "description": "Name given to the ride",
        "type": "string",
        'minLength': 2,
        'maxLength': 64
    }
    props["duration"] = {
        "description": "Ride duration in seconds",
        "type": "integer",
        "pattern": "^[1-9]"
    }
    props["datetime"] = {
        "description": "Date and time the ride started",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"   # noqa: E501
    }
    return schema
