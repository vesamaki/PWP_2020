'''
This app is a simple human operated restful API client designed to be used
with PWP-course cycling equipment API.
It works with the assumption, that link relations which are promised in the
API resource state diagram are present in the representations sent by the API.
Furthermore it trusts that the API will not send broken hypermedia controls or
JSON schema.
Must use HTTP-protocol. HTTPS is not supported.
'''

# Library imports
import requests
from json import JSONDecodeError

# Project imports
from utils import APIError, extract_prev_href, print_line, \
                  api_entry, \
                  process_body, \
                  get_resource, post_resource, put_resource, delete_resource


def main():
    '''
    The main application. Purpose is to cycle around the functions used to
    interract with the API in a forever-loop. Exits loop and terminates
    application, when variables href, method and schema are set as None.

    No return value.

    Exceptions. All API calls are done over a requests session. If any
    exceptions specific to the session are caught, then the application
    restarts from entry point. Any API specific exceptions are caught within
    the method handling the app continues from a state before the API call,
    caused the exception.

    ConnectionError             In case of a connection error of the TCP/IP
                                stack.
    requests.Timeout            If a timeout occured with the HTTP request.
    requests.TooManyRedirects   In case the request experiences too many
                                redirects.

    APIError                    In case the API replies with any != 2xx status
                                code
    '''

    breakout = False
    while True and not breakout:
        with requests.Session() as s:
            SERVER_URL, href, method = api_entry(s)
            SERVER_URL = SERVER_URL.strip("/api/")
            # print("DEBUG MAIN:\t\tFull URL: ", SERVER_URL + href, "\r\n")
            try:
                body = None
                while True:
                    if body is not None:
                        # Print UI
                        print_line()
                        print("\r\nCurrent route: {}".format(href))
                        href, method, schema = process_body(body)
                        # print("DEBUG MAIN:\t\thref after process is: ", href)
                        # print("DEBUG MAIN:\t\tmethod after"
                        #       "process is: ", method)
                    if method == "get":
                        # print("DEBUG MAIN:\t\thref for GET is: ", href)
                        # print("DEBUG MAIN:\t\tGETting: ", SERVER_URL + href)
                        try:
                            # Resfresh UI
                            get_body = get_resource(s, SERVER_URL + href)
                        except APIError as err:
                            print("\n", err)
                            input("Press Enter to continue...")
                        except JSONDecodeError:
                            print("Server response was not a "
                                  "valid JSON document.")
                            input("Press Enter to continue...")
                        else:
                            body = get_body
                    elif method == "post":
                        # print("DEBUG MAIN:\t\thref for POST is: ", href)
                        # print("DEBUG MAIN:\t\tPOSTing: ", SERVER_URL + href)
                        try:
                            # Post new resource
                            resp = post_resource(s, SERVER_URL + href, schema)
                            if resp.status_code == 201:
                                print("\r\nResource created: ",
                                      resp.headers["Location"].strip(SERVER_URL)  # noqa: E501
                                      )
                                # Ask user to get data on newly created
                                # resource, or stay at current resource-state
                                while True:
                                    str_in = input("\r\nExamine newly created "
                                                   "resource? (y/n): ") \
                                                   .strip().lower()
                                    if str_in == "y":
                                        # Get newly created resource data
                                        # and return body
                                        body = get_resource(s, resp.headers["Location"])  # noqa: E501
                                        break
                                    elif str_in == "n":
                                        # Resfresh UI
                                        body = get_resource(s, SERVER_URL + href)  # noqa: E501
                                        break
                                    else:
                                        print("Select \"y\" for yes or "
                                              "\"n\n for no, please.")
                            else:
                                raise APIError(resp.status_code, resp.content)
                        except APIError as err:
                            print("\n", err)
                            input("Press Enter to continue...")
                    elif method == "put":
                        # print("DEBUG MAIN:\t\thref for PUT is: ", href)
                        # print("DEBUG MAIN:\t\tPUTing: ", SERVER_URL + href)
                        try:
                            # Make changes
                            resp = put_resource(s, SERVER_URL + href, schema)
                            if resp.status_code == 204:
                                print("\r\nResource modified: ", href)
                                # Resfresh UI
                                print("Refreshing UI...")
                                body = get_resource(s, SERVER_URL + href)
                            else:
                                raise APIError(resp.status_code, resp.content)
                        except APIError as err:
                            print("\n", err)
                            input("Press Enter to continue...")
                    elif method == "delete":
                        # print("DEBUG MAIN:\t\thref for DELETE is: ", href)
                        # print("DEBUG MAIN:\t\tDELETing: ", SERVER_URL + href)
                        try:
                            # Delete resource
                            resp = delete_resource(s, SERVER_URL + href)
                            if resp.status_code == 204:
                                print("\r\nResource deleted: ", href)
                                # If successfull, go back one level in href
                                href = extract_prev_href(href)
                                print("Falling back to parent resource...")
                                body = get_resource(s, SERVER_URL + href)
                            else:
                                raise APIError(resp.status_code, resp.content)
                        except APIError as err:
                            print("\n", err)
                            input("Press Enter to continue...")
                    # Terminates program
                    elif href is None and method is None and schema is None:
                        breakout = True
                        break
            except ConnectionError:
                print("Get request to {} experienced a connection error."
                      .format(SERVER_URL + href)
                      )
                input("Press Enter to continue...")
            except requests.Timeout:
                print("Get request to {} timed out.".format(SERVER_URL + href))
                input("Press Enter to continue...")
            except requests.TooManyRedirects:
                print("Get request to {} experienced too many redirects."
                      .format(SERVER_URL + href)
                      )
                input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
        print("\r\nGood bye!")
    except KeyboardInterrupt:
        print("\r\n\r\nProgram terminated by Ctrl + C.")
