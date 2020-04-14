'''
Docstring to utils
'''

# Library imports
from flask import json, url_for, request, Response
from jsonschema import validate, ValidationError

# Project imports
from cyequ.constants import MASON, ERROR_PROFILE
from cyequ.static.schemas.user_schema import user_schema
from cyequ.static.schemas.equipment_schema import equipment_schema
from cyequ.static.schemas.component_schema import component_schema
# from cyequ.static.schemas.ride_schema import ride_schema


class MasonBuilder(dict):
    '''
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    '''

    def add_error(self, title, details):
        '''
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        '''

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        '''
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        '''

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        '''
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        '''

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class CommonBuilder(MasonBuilder):
    '''
    Class docstring here
    '''

    def add_control_all_users(self):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:users-all",
            href=url_for("api.usercollection"),
            method="GET",
            encoding="json",
            title="Get a list of all users known to the API."
        )

    def add_control_all_equipment(self, user):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:equipment-owned",
            href=url_for("api.equipmentbyuser", user=user),
            method="GET",
            encoding="json",
            title="A list of all equipment owned by the given user's name."
        )


class UserBuilder(CommonBuilder):
    '''
    Class docstring here
    '''

    def add_control_add_user(self):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:add-user",
            href=url_for("api.usercollection"),
            method="POST",
            encoding="json",
            title="Adds a new user.",
            schema=user_schema()
        )

    def add_control_edit_user(self, user):
        '''
        Docstring here
        '''

        self.add_control(
            "edit",
            href=url_for("api.useritem", user=user),
            method="PUT",
            encoding="json",
            title="Edits user's information",
            schema=user_schema()
        )


class EquipmentBuilder(CommonBuilder):
    '''
    Class docstring here
    '''

    def add_control_add_equipment(self, user):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:add-equipment",
            href=url_for("api.equipmentbyuser", user=user),
            method="POST",
            encoding="json",
            title="Adds a new equipment for the user.",
            schema=equipment_schema()
        )

    def add_control_add_component(self, user, equipment):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:add-component",
            href=url_for("api.equipmentitem", user=user, equipment=equipment),
            method="POST",
            encoding="json",
            title="Adds a new component to the associated equipment.",
            schema=equipment_schema()
        )

    def add_control_edit_equipment(self, user, equipment):
        '''
        Docstring here
        '''

        self.add_control(
            "edit",
            href=url_for("api.equipmentitem", user=user, equipment=equipment),
            method="PUT",
            encoding="json",
            title="Edits equipment's information",
            schema=equipment_schema()
        )

    def add_control_delete_equipment(self, user, equipment):
        '''
        Docstring here
        '''

        self.add_control(
            "cyequ:delete",
            href=url_for("api.equipmentitem", user=user, equipment=equipment),
            method="DELETE",
            title="Deletes this equipment"
        )


class ComponentBuilder(CommonBuilder):
    '''
    Class docstring here
    '''

    def add_control_edit_component(self, user, equipment, component):
        '''
        Docstring here
        '''
        self.add_control(
            "edit",
            href=url_for("api.componentitem",
                         user=user,
                         equipment=equipment,
                         component=component),
            method="PUT",
            encoding="json",
            title="Edits component's information",
            schema=component_schema()
        )

    def add_control_delete_component(self, user, equipment, component):
        '''
        Docstring here
        '''
        self.add_control(
            "cyequ:delete",
            href=url_for("api.componentitem",
                         user=user,
                         equipment=equipment,
                         component=component),
            method="DELETE",
            title="Deletes component of the associated equipment."
        )


def create_error_response(status_code, title, message=None):
    '''
    Docstring here
    '''

    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)


def check_for_json(request):
    '''
    Docstring here
    '''

    if not request:
        return create_error_response(415, "Unsupported media type",
                                     "Requests must be JSON"
                                     )


def validate_request_to_schema(request, schema):
    '''
    Docstring here
    '''
    try:
        validate(request, schema)
    except ValidationError as err:
        return create_error_response(400, "Invalid JSON "
                                     "document", str(err))


def check_db_existance(kwrd, db_object):
    '''
    Find keyword in database. If not found, respond with error
    '''

    if db_object is None:
        return create_error_response(404, "Not found",
                                     "No instance was found with the"
                                     " keyword {}".format(kwrd)
                                     )
    return db_object
