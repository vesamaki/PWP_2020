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
        print("Full URL: ", SERVER_URL + href)
    #    print("(R)akenna kokoelma")
    #    print("(L)isää uusia levyjä")
    #    print("(M)uokkaa levyjä")
    #    print("(P)oista levyjä")
    #    print("(J)ärjestä kokoelma")
    #    print("(T)ulosta kokoelma")
    #    print("(Q)uittaa")
        while True:
            if method == "get":
                body = get_resource(s, SERVER_URL + href)
            if body is not None:
                process_body(body)
            cont = input("Run again? (y/n): ")
            if cont != "y":
                break


if __name__ == "__main__":
    try:
        main()
        print("Good bye!")
    except KeyboardInterrupt:
        print("Ohjelma keskeytettiin, kokoelmaa ei tallennettu")
