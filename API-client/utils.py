'''
This module provides utility functions for the API-client
'''

import requests
import json
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


# From PWP-course EX4 mumeta-submit.py:
def submit_data(s, api_url, ctrl, data):
    """
    submit_data(s, ctrl, data) -> requests.Response

    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI and HTTP method defined in the *ctrl* dictionary
    (a Mason @control). The data is serialized by this function and sent to
    the API.

    Returns the response object provided by requests.
    """

    resp = s.request(ctrl["method"],
                     api_url + ctrl["href"],
                     data=json.dumps(data),
                     headers={"Content-type": "application/json"}
                     )
    return resp


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
    # body_copy = [val for val in body_copy if val in ["@namespaces", "@controls", "items"]]  # noqa: E501
    # Print the response base data, if any
    for key in body_copy.keys():
        print("{}: {}".format(key, body_copy[key]))
    # Then process and print available @controls for this resource
    # For our RESTful API, @controls should always be included in response body
    print("Controls available with this resource: ")
    for ctrl in body["@controls"].keys():
        print("Link relation: {}".format(ctrl), end="")
        for attr in body["@controls"][ctrl]:
            if attr not in ["schema"]:
                print("\t", end="")
                print("{}: {}".format(attr, body["@controls"][ctrl][attr]),
                      end=""
                      )
        print("")
    print("\r\n")
    # Since the items' list could be very long, process and print any items
    # included in response as the last part
    for ind in body["items"]:
        for key in ind.keys():
            if key != "@controls":
                print(key)
                # print("{}: {}".format(key, body["items"][key]))



#    return href, method


def get_resource(s, href):
    '''
    Function for GET-request.
    Returns request body, or
    raises APIError exception if response status_code is other than 200 and
    returns None.
    '''

    resp = s.get(href)
    if resp.status_code != 200:
        raise APIError(resp.status_code, resp.content)
    else:
        return resp.json()


def post_resource(s, href, schema):
    '''
    Function for POST-request.
    Returns newly created resource's GET-request body, or
    raises APIError exception if response status_code is other than 201 and
    returns None.
    '''

    # Build POST according to provided schema
    # See submit_data -function
    data = []
    # Then post
    resp = s.post(href, json=data)
    if resp.status_code == 201:
        # Resp location header has href for newly created resource
        # Get newly created resource data and return body
        resp = get_resource(s, resp.headers["Location"])
    else:
        raise APIError(resp.status_code, resp.content)
    # Ask user to get data on newly created resource,
    # or stay at current resource-state
    while True:
        str_in = input("Examine newly created resource? (y/n): ") \
                    .strip().lower()
        if str_in == "y":
            return resp.json()
        elif str_in == "n":
            return None
        else:
            print("Select \"y\" for yes or \"n\n for no, please.")


def put_resource(s, href, schema):
    '''
    Function for PUT-request.
    Raises APIError exception if response status_code is other than 204.
    Returns None.
    '''

    # Build PUT according to provided schema
    # See submit_data -function
    data = []
    # Then put
    resp = s.put(href, json=data)
    if resp.status_code != 204:
        raise APIError(resp.status_code, resp.content)


def delete_resource(s, href):
    '''
    Function for DELETE-request.
    Raises APIError exception if response status_code is other than 204.
    Returns None.
    '''

    resp = s.delete(href)
    if resp.status_code != 204:
        raise APIError(resp.status_code, resp.content)
