



"""
@app.route("/products/add/", methods=["POST"])
def add_product():
    if request.method == "POST":
        try:
            # Get string from request by "keyword"
            rq_handle = request.json["handle"]
            rq_weight = float(request.json["weight"])
            rq_price = float(request.json["price"])
            # If empty string
            if not rq_handle:
                raise KeyError
            # Query the product database for given handle
            db_handle = Product.query.filter_by(handle=rq_handle).first()
            # If no match, then it's a new product, else abort
            if db_handle is None:
                new_prod = Product(
                    handle=rq_handle,
                    weight=rq_weight,
                    price=rq_price
                    )
                db.session.add(new_prod)
                db.session.commit()
            else:
                abort(409, description="Handle already exists")
        except (TypeError, BadRequest):
            # Checks against request body when calling request.json
            #   and if Content-Type header is not application/json
            abort(415, description="Request content type must be JSON")
        except KeyError:
            abort(400, description="Incomplete request - missing fields")
        except ValueError:
            abort(400, description="Weight and price must be numbers")
        except IntegrityError:
            # In case of some database error
            db.session.rollback()
            abort(400, description="Database IntegrityError")
    else:
        abort(405, description="POST method required")
    return "Successful", 201
"""
"""
@app.route("/storage/<product>/add/", methods=["POST"])
def add_to_storage(product):
    if request.method == "POST":
        try:
            # Query for product in database by handle in request body
            db_handle = Product.query.filter_by(handle=product).first()
            # If exists, add new storage entry, else abort
            if db_handle is not None:
                rq_location = request.json["location"]
                rq_qty = int(request.json["qty"])
                # Can't have location string empty or qty zero
                if not rq_location or rq_qty == 0:
                    raise KeyError
                new_entry = StorageItem(
                    qty=rq_qty,
                    location=rq_location,
                    product_id=db_handle.id
                    )
                db.session.add(new_entry)
                db.session.commit()
            else:
                abort(404, description="Product not found")
        except (TypeError, BadRequest):
            abort(415, description="Request content type must be JSON")
        except KeyError:
            abort(400, description="Incomplete request - missing fields")
        except ValueError:
            abort(400, description="Qty must be an integer")
        except IntegrityError:
            db.session.rollback()
            abort(400, description="Database IntegrityError")
    else:
        abort(405, description="POST method required")
    return "Successful", 201
"""
"""
@app.route("/storage/", methods=["GET"])
def get_inventory():
    if request.method == "GET":
        # Initialize inventory list
        inv_list = []
        # Enable access to each product row entries. I.e prod[0]
        prod = db.session.query(Product)
        # Check how many products in database
        cnt_prod = prod.count()
        # Loop through each product
        for i in range(cnt_prod):
            # Enable access to storage entries of each product
            stor = db.session.query(StorageItem).filter(StorageItem.product == prod[i])
            # Check how many storage entries for this product
            cnt_stor = stor.count()
            # Initialize a list the size of storage entry count (None-filled)
            sto_list = [None] * cnt_stor
            # Loop through each storage entry and add tuples to list
            for j in range(cnt_stor):
                sto_list[j] = (stor[j].location, stor[j].qty)
                # Didn't work for some reason:
                #sto_list.append((stor[j].location, stor[j].qty))
            # For each product, append to the inventory list a dict
            #   including product data and the list of storage tuples
            inv_list.append({'handle': prod[i].handle,
                             'weight': prod[i].weight,
                             'price': prod[i].price,
                             'inventory': sto_list
                             })
    else:
        abort(405, description="GET method required")
    # Return jsonified list
    return json.dumps(inv_list)
"""
