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
from utils import APIError, submit_data, \
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
            while True and not breakout:
                if method == "get":
                    print("DEBUG MAIN:\t\thref for GET is: ", href)
                    print("DEBUG MAIN:\t\tGETting: ", SERVER_URL + href)
                    body = get_resource(s, SERVER_URL + href)
                if body is not None:
                    href, method, schema = process_body(body)
                    print("DEBUG MAIN:\t\thref after process is: ", href)
                    print("DEBUG MAIN:\t\tmethod after process is: ", method)
                if href is None and method is None and schema is None:
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
