'''
This module defines the json schemas for Cycling Equipment Usage API

'''


def user_schema():
'''
Defines the user schema
'''
    schema = {
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
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"
    }
    props["date_retired"] = {
        "description": "Date and time the equipment was taken to service",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"
    }
    return schema    
        
def component_schema():
'''
Defines the component schema
'''
    schema = {
        "type": "object",
        "required": ["name", "category", "brand", "model", "date_added"]
    }
    props = schema["properties"] = {}
    props["name"] = {
        "description": "Name of component",
        "type": "string",
        'minLength': 2,
        'maxLength': 64
    }
    props["category"] = {
        "description": "Component category",
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
        "description": "Date and time the component was taken to service",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"
    }
    props["date_retired"] = {
        "description": "Date and time the component was taken to service",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"
    }
    return schema
    
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
        "type": "number"
    }
    props["datetime"] = {
        "description": "Date and time the ride started",
        "type": "string",
        "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]\s[0-2][0-4]:[0-5][0-9]:[0-5][0-9]$"
    }
    return schema
    
    