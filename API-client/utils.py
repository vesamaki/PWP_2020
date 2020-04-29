'''
This module provides utility functions for the API-client
'''

import requests
import json
import re
from json import JSONDecodeError


# From PWP-course EX4 mumeta-submit.py
class APIError(Exception):
    """
    Exception class used when the API responds with an error code. Gives
    information about the error in the console.
    """

    def __init__(self, code, error):
        """
        Initializes the exception with *code* as the status code from
        the response and *error* as the response body.
        """

        self.error = json.loads(error)
        self.code = code

    def __str__(self):
        """
        Returns all details from the error response sent by the API formatted
        into a string.
        """

        return "Error {code} while accessing {uri}: {msg}\nDetails:\n{msgs}" \
               .format(code=self.code,
                       uri=self.error["resource_url"],
                       msg=self.error["@error"]["@message"],
                       msgs="\n".join(self.error["@error"]["@messages"])
                       )


def print_line():
    for i in range(81):
        print("-", end="")
    else:
        print("")


def api_entry(s):
    while True:
        server_url = input("Enter API URL: ")
        if server_url.startswith("http://"):
            if server_url.endswith("/api/"):
                break
            else:
                print("API URL didn't end with \"/api/\".")
        else:
            print("API URL didn't start with \"http://\".")
    try:
        resp = s.get(server_url, timeout=5)
        if resp.status_code != 200:
            print("Unable to access API")
        else:
            try:
                # body = json.loads(resp.data)
                body = resp.json()
                # Getting the first API resource, fixed to cyequ:users-all
                for item in body["@controls"]:
                    if item == "cyequ:users-all":
                        href = body["@controls"]["cyequ:users-all"]["href"]
                        method = body["@controls"]["cyequ:users-all"]["method"] \
                            .lower()
                    else:
                        href, method = None
                        print("Link relation \"cyequ:users-all\""
                              "not found."
                              )
            except JSONDecodeError:
                print("Server response was not a valid JSON document.")
            except KeyError:
                print("\"@controls\" not found for API. Sure this is a"
                      "RESTful-API?"
                      )
    except ConnectionError:
        print("Get request to {} experienced a connection error."
              .format(server_url)
              )
    except requests.Timeout:
        print("Get request to {} timed out.".format(server_url))
    except requests.TooManyRedirects:
        print("Get request to {} experienced too many redirects."
              .format(server_url)
              )
    return server_url, href, method


def process_body(body):
    '''
    This function will print any response base data, as well as controls, and
    provides user input queries for next resource action.
    Returns href and method for the next resource.
    '''

    # To first print resource base data,
    # make a copy of body and leave out namespaces, controls and
    # items before print
    body_copy = dict(body)
    try:
        body_copy.pop("@namespaces")
        body_copy.pop("@controls")
        body_copy.pop("items")
    except KeyError:
        pass
    # Print the response base data, if any
    if body_copy.keys():
        print("\r\nResource data:")
    for key in body_copy.keys():
        print("\t{}: {}".format(key, body_copy[key]))
    # Then process and print available @controls for this resource
    # For our RESTful API, @controls should always be included in response body
    print("\r\nControls available with this resource: ")
    for ctrl in body["@controls"].keys():
        print("Link relation - name: {}".format(ctrl), end="")
        for attr in body["@controls"][ctrl]:
            if attr not in ["schema"]:
                if attr not in ["profile"]:
                    print("\n\t\t{}: {}".format(attr,
                                                body["@controls"][ctrl][attr]
                                                ),
                          end=""
                          )
        print("\n")
    # Process items list if included
    # Since the items' list could be very long, process and print any items
    # included in response as the last part
    if "items" in body:
        print("\r\nResource's items:")
        for i, val in enumerate(body["items"]):
            print("[{}]".format(i+1), end="")
            for key in val.keys():
                # Print data of each item
                if key != "@controls":
                    print("\t{}: {}".format(key, body["items"][i][key]))
                # Print link relation "self" for each item
                else:
                    for ctrl in body["items"][i][key].keys():
                        if ctrl == "self":
                            href_list = body["items"][i][key][ctrl]["href"] \
                                        .split("/")
                            # Match kwrd to second last.
                            # The last is "" (empty string) from href-
                            # split method.
                            kwrd = href_list[-2]
                            print("\tLink relation - \tname: "
                                  "{}\n\t\t\t\tURI: {}\n\t\t\t\thref: {}"
                                  .format(ctrl,
                                          kwrd,
                                          body["items"][i][key][ctrl]["href"]
                                          )
                                  )
            print("")
    else:
        print("\r\nResource has no item data.")
    # User selection for next resource + method
    breakout, no_match = False, False
    while True and not breakout:
        print("\r\nType in the next link relation name for top-level, "
              "or for any listed items input item's URI"
              "\nTerminate program with 'q'"
              )
        kwrd = input("\r\nType in your selection: ")
        print("DEBUG:\t\tInput kwrd: ", kwrd)
        if kwrd.lower() == "q":
            print("DEBUG:\t\tInput kwrd was 'q'")
            href, method, schema = None, None, None
            break
        elif kwrd in body["@controls"].keys():
            href = body["@controls"][kwrd]["href"]
            print("DEBUG:\t\tSaving body-control href")
            # Check if method given
            if "method" in body["@controls"][kwrd].keys():
                method = body["@controls"][kwrd]["method"].lower()
            else:
                # If no method given for a control, assume it's GET
                method = "get"
            # Check if schema given
            if "schema" in body["@controls"][kwrd].keys():
                schema = body["@controls"][kwrd]["schema"]
            else:
                schema = None
            print("DEBUG:\t\tBreak from body-controls")
            break
        # Make sure response body includes "items" list
        elif "items" in body:
            # Search each item dict for match to input kwrd
            for item in body["items"]:
                href_list = item["@controls"]["self"]["href"].split("/")
                # Match kwrd to second last. The last is "" (empty string)
                # from href split method.
                if kwrd == href_list[-2]:
                    href = item["@controls"]["self"]["href"]
                    # Check if method given
                    if "method" in item["@controls"]["self"]:
                        method = item["@controls"]["self"]["method"].lower()
                    else:
                        # if no method given for a control,
                        # assume it's GET
                        method = "get"
                    # Check if schema given
                    if "schema" in item["@controls"]["self"]:
                        schema = item["@controls"]["self"]["schema"]
                    else:
                        schema = None
                    breakout = True
                    break
            else:
                no_match = True
        else:
            no_match = True
        if no_match:
            no_match = False
            print("\nYour input didn't match any link relation. Try again or "
                  "type 'q' to quit.\n")
    print("DEBUG:\t\thref is now: ", href)
    print("DEBUG:\t\tmethod is now: ", method)
    if schema:
        print("DEBUG:\t\tSchema is not None")
    else:
        print("DEBUG:\t\tschema is now: ", schema)
    return href, method, schema


def get_resource(s, href):
    '''
    Function for GET-request.
    Returns request body, or
    raises APIError exception if response status_code is other than 200 and
    returns None.
    '''

    try:
        resp = s.get(href)
        print("DEBUG GET:\t\tStatus code: ", resp.status_code)
        if resp.status_code == 302:
            href = resp.headers["Location"]
            print("This links to ", href)
        if resp.status_code != 200:
            raise APIError(resp.status_code, resp.content)
        else:
            return resp.json()
    except JSONDecodeError:
        print("Server response was not a valid JSON document.")
        return None
    except KeyError:
        print("\"@controls\" not found for API. Sure this is a"
              "RESTful-API?"
              )


def ask_input(key, type):
    return input("Give value for '{}' of type '{}': "
                 .format(key, type)
                 )


def post_resource(s, href, schema):
    '''
    Function for POST-request.
    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI. The data is serialized by this function and sent to
    the API.

    Returns newly created resource's response object provided by requests.
    '''

    # Build POST base according to provided schema
    # See submit_data -function
    data = {}
    # Generate difference list between all properties and required properties
    props_list = []
    for key in schema["properties"].keys():
        props_list.append(key)
    # Courtesy of Mark Byers @ https://stackoverflow.com/questions/3462143/get-difference-between-two-lists  # noqa: E501
    req_set = set(schema["required"])
    opt_props = [x for x in props_list if x not in req_set]
    # Three possible POSTS: UserCollection, UserItem, EquipmentItem
    # Input data for each schema-property
    print("\nCreate new resource.\n")
    # POST UserCollection uses user-schema
    if schema["title"] == "User schema":
        for key in schema["required"]:
            while True:
                value = ask_input(key, schema["properties"][key]["type"])
                # Test for type
                if len(value) >= 2 and len(value) <= 64:
                    break
                else:
                    print("Input must be between 2 and 64 characters long")
            data[key] = value
        # Ask for optionals
        if opt_props:
            while True:
                ans = "n"
                # ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    # No optional properties in user_schema
                    for key in opt_props:
                        pass
    # POST UserItem uses equipment schema
    elif schema["title"] == "Equipment schema":
        for key in schema["required"]:
            if key in ["name", "category", "brand"]:
                while True:
                    value = ask_input(key,
                                           schema["properties"][key]["type"]
                                           )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 64:
                        break
                    else:
                        print("Input must be between 2 and 64 characters long")
                data[key] = value
            elif key in ["model"]:
                while True:
                    value = ask_input(key,
                                           schema["properties"][key]["type"]
                                           )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 128:
                        break
                    else:
                        print("Input must be between 2 and "
                              "128 characters long")
                data[key] = value
            elif key in ["date_added"]:
                while True:
                    print("Give date and time in format "
                          "'YYYY-MM-DD hh:mm:ss'.")
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for pattern
                    if re.match(schema["properties"][key]["pattern"], value):
                        break
                    else:
                        print("Input must be format 'YYYY-MM-DD hh:mm:ss'.")
                data[key] = value
        # Ask for optionals
        else:
            while True:
                ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    for key in opt_props:
                        if key in ["date_retired"]:
                            while True:
                                print("Give date and time in format "
                                      "'YYYY-MM-DD hh:mm:ss'.")
                                value = ask_input(key, schema["properties"][key]["type"])  # noqa: E501
                                # Test for pattern
                                if re.match(schema["properties"][key]["pattern"], value):  # noqa: E501
                                    break
                                else:
                                    print("Input must be format "
                                          "'YYYY-MM-DD hh:mm:ss'.")
                            data[key] = value
                    break
    # POST EquipmentItem uses component schema
    elif schema["title"] == "Component schema":
        for key in schema["required"]:
            if key in ["name", "category", "brand"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 64:
                        break
                    else:
                        print("Input must be between 2 and 64 characters long")
                data[key] = value
            elif key in ["model"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 128:
                        break
                    else:
                        print("Input must be between 2 and "
                              "128 characters long")
                data[key] = value
            elif key in ["date_added"]:
                while True:
                    print("Give date and time in format "
                          "'YYYY-MM-DD hh:mm:ss'.")
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for pattern
                    if re.match(schema["properties"][key]["pattern"], value):
                        break
                    else:
                        print("Input must be format 'YYYY-MM-DD hh:mm:ss'.")
                data[key] = value
        # Ask for optionals
        else:
            while True:
                ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    for key in opt_props:
                        if key in ["date_retired"]:
                            while True:
                                print("Give date and time in format "
                                      "'YYYY-MM-DD hh:mm:ss'.")
                                value = ask_input(key, schema["properties"][key]["type"])  # noqa: E501
                                # Test for pattern
                                if re.match(schema["properties"][key]["pattern"], value):  # noqa: E501
                                    break
                                else:
                                    print("Input must be format "
                                          "'YYYY-MM-DD hh:mm:ss'.")
                            data[key] = value
                    break
    # Then post
    resp = s.post(href,
                  data=json.dumps(data),
                  headers={"Content-type": "application/json"}
                  )
    return resp


def put_resource(s, href, schema):
    '''
    Function for PUT-request.
    Raises APIError exception if response status_code is other than 204.
    Returns None.
    '''

    # Build PUT according to provided schema
    data = {}
    # Generate difference list between all properties and required properties
    props_list = []
    for key in schema["properties"].keys():
        props_list.append(key)
    # Courtesy of Mark Byers @ https://stackoverflow.com/questions/3462143/get-difference-between-two-lists  # noqa: E501
    req_set = set(schema["required"])
    opt_props = [x for x in props_list if x not in req_set]
    # Three possible PUTs: UserItem, EquipmentItem, ComponentItem
    # Input data for each schema-property
    print("\nModify resource.\n")
    # PUT UserItem uses user-schema
    if schema["title"] == "User schema":
        for key in schema["required"]:
            while True:
                value = ask_input(key, schema["properties"][key]["type"])
                # Test for type
                if len(value) >= 2 and len(value) <= 64:
                    break
                else:
                    print("Input must be between 2 and 64 characters long")
            data[key] = value
        # Ask for optionals
        if opt_props:
            while True:
                ans = "n"
                # ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    # No optional properties in user_schema
                    for key in opt_props:
                        pass
    # PUT EquipmentItem uses equipment schema
    elif schema["title"] == "Equipment schema":
        for key in schema["required"]:
            if key in ["name", "category", "brand"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 64:
                        break
                    else:
                        print("Input must be between 2 and 64 characters long")
                data[key] = value
            elif key in ["model"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 128:
                        break
                    else:
                        print("Input must be between 2 and "
                              "128 characters long")
                data[key] = value
            elif key in ["date_added"]:
                while True:
                    print("Give date and time in format "
                          "'YYYY-MM-DD hh:mm:ss'.")
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for pattern
                    if re.match(schema["properties"][key]["pattern"], value):
                        break
                    else:
                        print("Input must be format 'YYYY-MM-DD hh:mm:ss'.")
                data[key] = value
        # Ask for optionals
        else:
            while True:
                ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    for key in opt_props:
                        if key in ["date_retired"]:
                            while True:
                                print("Give date and time in format "
                                      "'YYYY-MM-DD hh:mm:ss'.")
                                value = ask_input(key, schema["properties"][key]["type"])  # noqa: E501
                                # Test for pattern
                                if re.match(schema["properties"][key]["pattern"], value):  # noqa: E501
                                    break
                                else:
                                    print("Input must be format "
                                          "'YYYY-MM-DD hh:mm:ss'.")
                            data[key] = value
                    break
    # PUT ComponentItem uses component schema
    elif schema["title"] == "Component schema":
        for key in schema["required"]:
            if key in ["name", "category", "brand"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 64:
                        break
                    else:
                        print("Input must be between 2 and 64 characters long")
                data[key] = value
            elif key in ["model"]:
                while True:
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for type
                    if len(value) >= 2 and len(value) <= 128:
                        break
                    else:
                        print("Input must be between 2 and "
                              "128 characters long")
                data[key] = value
            elif key in ["date_added"]:
                while True:
                    print("Give date and time in format "
                          "'YYYY-MM-DD hh:mm:ss'.")
                    value = ask_input(key,
                                      schema["properties"][key]["type"]
                                      )
                    # Test for pattern
                    if re.match(schema["properties"][key]["pattern"], value):
                        break
                    else:
                        print("Input must be format 'YYYY-MM-DD hh:mm:ss'.")
                data[key] = value
        # Ask for optionals
        else:
            while True:
                ans = input("Input optional values? (y/n): ")
                if ans == "n":
                    break
                elif ans == "y":
                    # Optionals listed in opt_props defined above
                    for key in opt_props:
                        if key in ["date_retired"]:
                            while True:
                                print("Give date and time in format "
                                      "'YYYY-MM-DD hh:mm:ss'.")
                                value = ask_input(key, schema["properties"][key]["type"])  # noqa: E501
                                # Test for pattern
                                if re.match(schema["properties"][key]["pattern"], value):  # noqa: E501
                                    break
                                else:
                                    print("Input must be format "
                                          "'YYYY-MM-DD hh:mm:ss'.")
                            data[key] = value
                    break
    # Then put
    resp = s.put(href,
                 data=json.dumps(data),
                 headers={"Content-type": "application/json"}
                 )
    return resp


def extract_prev_href(href):
    '''
    Extracts the "one level down" href of given API href based on "/".
    Only used with DELETE-method
    Returns processed new href.
    '''

    new_href = "/"
    # Split href to list by "/"
    href_list = href.split("/")
    # Construct new_href
    for val in href_list[1:-2]:
        new_href = new_href + val + "/"
    return new_href


def delete_resource(s, href):
    '''
    Function for DELETE-request.
    Raises APIError exception if response status_code is other than 204.
    Returns None.
    '''

    resp = s.delete(href)
    return resp
