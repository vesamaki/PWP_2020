'''
Docstring to component resource routes
'''


# Library imports
from Flask import url_for
from datetime import datetime

# Project imports
from cyequ.utils import MasonBuilder, CyequBuilder
from cyequ import api, models

class ComponentItem(Resource):

    def get(self, handle):
        # Check for request method
#        if request.method != "GET":
#            return create_error_response(405, "Not found",
#                "GET method required"
#            )
        # Find product by handle in database. If not found, respond with error
        db_prod = Product.query.filter_by(handle=handle).first()
        if db_prod is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the" \
                                         " name {}".format(handle)
                                         )
        # Instantiate response message body
        body = InventoryBuilder(
            handle=db_prod.handle,
            weight=db_prod.weight,
            price=db_prod.price
        )
        # Add general controls to message body
        body.add_control("self", api.url_for(ProductItem, handle=handle))
        body.add_control("profile", PRODUCT_PROFILE)
        body.add_control("collection", api.url_for(ProductCollection))
        body.add_control_edit_product(handle)
        body.add_control_delete_product(handle)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, handle):
        # Check for json
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        # Validate request against the schema
        try:
            validate(request.json, Product.get_schema())
        except ValidationError as err:
            return create_error_response(400, "Invalid JSON document", str(err))
        # Find product by handle in database. If not found, respond with error
        db_prod = Product.query.filter_by(handle=handle).first()
        if db_prod is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the given" \
                                         " handle {}".format(handle)
                                         )
        # Update product data
        db_prod.handle = request.json["handle"]
        db_prod.weight = request.json["weight"]
        db_prod.price = request.json["price"]
        try:
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(409, "Already exists",
                                         "Product with handle '{}' already " \
                                         "exists.".format(request.json["handle"])
                                         )
        return Response(status=204)

    def delete(self, handle):
        db_prod = Product.query.filter_by(handle=handle).first()
        if db_prod is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the " \
                                         "name {}".format(handle)
                                         )
        try:
            db.session.delete(db_prod)
            db.session.commit()
        except IntegrityError:
            # In case of database error
            db.session.rollback()
            return create_error_response(500, "Internal Server Error",
                                         "The server encountered an " \
                                         "unexpected condition that prevented" \
                                         " it from fulfilling the request."
                                         )
        return Response(status=204)
