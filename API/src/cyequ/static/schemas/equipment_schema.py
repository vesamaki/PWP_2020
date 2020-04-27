'''
This module defines the Equipment json schema for Cycling Equipment Usage API

'''


def equipment_schema():
    '''
    Defines the equipment schema
    '''

    schema = {
        "type": "object",
        "required": ["name", "category", "brand", "model", "date_added"]
    }
    props = schema["properties"] = {}
    props["name"] = {
        "description": "Name of equipment",
        "type": "string",
        'minLength': 2,
        'maxLength': 64
    }
    props["category"] = {
        "description": "Equipment category",
        "type": "string",
        'minLength': 2,
        'maxLength': 64
    }
    props["brand"] = {
        "description": "The brand-name of the manufacturer",
        "type": "string",
        'minLength': 1,
        'maxLength': 64
    }
    props["model"] = {
        "description": "The model-name given by the manufacturer",
        "type": "string",
        'minLength': 1,
        'maxLength': 128
    }
    props["date_added"] = {
        "description": "Date and time the equipment was taken to service",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"  # noqa: E501
    }
    props["date_retired"] = {
        "description": "Date and time the equipment was taken to service",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"  # noqa: E501
    }
    return schema
