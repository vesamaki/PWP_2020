'''
This app is a simple human operated restful API client designed to be used
with PWP-course cycling equipment API.
it works with the assumption that link relations that are promised in the
API resource state diagram are present in the representations sent by the API.
Furthermore it trusts that the API will not send broken hypermedia controls or
JSON schema.
Must use HTTP-protocol. HTTPS is not supported.
'''

# Library imports
import requests


# Project imports
from utils import APIError, extract_prev_href, print_line, \
                  api_entry, \
                  process_body, \
                  get_resource, post_resource, put_resource, delete_resource


def main():
    with requests.Session() as s:
        SERVER_URL, href, method = api_entry(s)
        SERVER_URL = SERVER_URL.strip("/api/")
        print("DEBUG MAIN:\t\tFull URL: ", SERVER_URL + href, "\r\n")
        breakout = False
        try:
            body = None
            while True and not breakout:
                if body is not None:
                    # Print UI
                    print_line()
                    print("\r\nCurrent route: {}".format(href))
                    href, method, schema = process_body(body)
                    print("DEBUG MAIN:\t\thref after process is: ", href)
                    print("DEBUG MAIN:\t\tmethod after process is: ", method)
                if method == "get":
                    print("DEBUG MAIN:\t\thref for GET is: ", href)
                    print("DEBUG MAIN:\t\tGETting: ", SERVER_URL + href)
                    try:
                        # Resfresh UI
                        body = get_resource(s, SERVER_URL + href)
                    except APIError as err:
                        print("\n", err)
                        input("Press Enter to continue...")
                elif method == "post":
                    print("DEBUG MAIN:\t\thref for POST is: ", href)
                    print("DEBUG MAIN:\t\tPOSTing: ", SERVER_URL + href)
                    try:
                        # Post new resource
                        resp = post_resource(s, SERVER_URL + href, schema)
                        if resp.status_code == 201:
                            print("\r\nResource created: ",
                                  resp.headers["Location"].strip(SERVER_URL)
                                  )
                            # Ask user to get data on newly created resource,
                            # or stay at current resource-state
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
                                    body = get_resource(s, SERVER_URL + href)
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
                    print("DEBUG MAIN:\t\thref for PUT is: ", href)
                    print("DEBUG MAIN:\t\tPUTing: ", SERVER_URL + href)
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
                    print("DEBUG MAIN:\t\thref for DELETE is: ", href)
                    print("DEBUG MAIN:\t\tDELETing: ", SERVER_URL + href)
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
        except requests.Timeout:
            print("Get request to {} timed out.".format(SERVER_URL + href))
        except requests.TooManyRedirects:
            print("Get request to {} experienced too many redirects."
                  .format(SERVER_URL + href)
                  )


if __name__ == "__main__":
    try:
        main()
        print("Good bye!")
    except KeyboardInterrupt:
        print("\r\n\r\nProgram terminated by Ctrl + C.")
