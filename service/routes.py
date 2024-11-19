######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shopcart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcart
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.models import Shopcart, Item  # pylint: disable=cyclic-import
from service.common import status  # HTTP Status Codes
from . import api  # pylint: disable=cyclic-import


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
# TODO: Update this route when prefix is added to the api # pylint: disable=W0511
# @app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    """Send ecommerce manager page file at index endpoint"""
    return app.send_static_file("index.html")


# Define the Item model
create_item_model = api.model(
    "Item",
    {
        "shopcart_id": fields.Integer(
            required=True, description="The ID of the shopcart this item belongs to"
        ),
        "name": fields.String(required=True, description="The name of the item"),
        "description": fields.String(
            required=True, description="A description of the item"
        ),
        "price": fields.Float(required=True, description="The price of the item"),
        "quantity": fields.Integer(
            required=True, description="The quantity of the item"
        ),
        "is_urgent": fields.Boolean(
            default=False, description="Indicates whether the item is urgent"
        ),
        "created_at": fields.DateTime(
            description="The date and time the item was created"
        ),
        "last_updated": fields.DateTime(
            description="The date and time the item was last updated"
        ),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        )
    },
)

# Define the Shopcart model
create_shopcart_model = api.model(
    "Shopcart",
    {
        "customer_name": fields.String(
            required=True, description="The name of the customer"
        ),
        "items": fields.List(
            fields.Nested(item_model), description="The list of items in the shopcart"
        ),
        "created_at": fields.DateTime(
            description="The date and time the shopcart was created"
        ),
        "last_updated": fields.DateTime(
            description="The date and time the shopcart was last updated"
        ),
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    create_shopcart_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        )
    },
)

# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "customer-name",
    type=str,
    location="args",
    required=False,
    help="The name of the customer",
)

item_args = reqparse.RequestParser()
item_args.add_argument(
    "name", type=str, location="args", required=False, help="The name of the item"
)


######################################################################
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """Returns all of the Shopcarts"""
        app.logger.info("Request to list Shopcarts...")

        shopcarts = []
        # Process the query string if any
        name = request.args.get("customer-name")
        if name:
            shopcarts = Shopcart.find_by_customer_name(name)
        else:
            shopcarts = Shopcart.all()

        results = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info("Returning %d shopcarts", len(results))
        return results, status.HTTP_200_OK

    @api.doc("create_shopcarts")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Creates a Shopcart
        This endpoint will create a Shopcart based the data in the body that is posted
        """
        app.logger.info("Request to Create a Shopcart")
        shopcart = Shopcart()
        app.logger.debug("Payload = %s", api.payload)
        shopcart.deserialize(api.payload)
        shopcart.create()
        app.logger.info("Shopcart with new id [%s] created!", shopcart.id)
        # TODO: Update the line below when ShopcartCollection is defined # pylint: disable=W0511
        location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)
        # location_url = api.url_for(ShopcartCollection, shopcart_id=shopcart.id, _external=True)
        return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", shopcart_id)

    # Retrieve the shopcart to delete and delete it if it exists
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        shopcart.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based on the body that is posted
    """
    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Update from the json in the body of the request
    updated_json = request.get_json()
    # if "items" not in updated_json:
    #     updated_json["items"] = shopcart.serialize()["items"]
    shopcart.deserialize(updated_json)
    shopcart.id = shopcart_id
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# ADD AN ITEM TO A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def create_items(shopcart_id):
    """
    Create an Item on a Shopcart

    This endpoint will add an item to a shopcart
    """
    app.logger.info("Request to create an Item for Shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart: Shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())
    item.shopcart_id = shopcart_id

    # Append the item to the shopcart
    shopcart.items.append(item)
    shopcart.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "get_items", shopcart_id=shopcart.id, item_id=item.id, _external=True
    )
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE ALL ITEMS FROM A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """
    Retrieve all Items from a Shopcart

    This endpoint will return all items for a specific shopcart based on its id
    """
    app.logger.info("Request for all items in Shopcart with id: %s", shopcart_id)

    # Find the shopcart by its ID, return 404 if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Process the query string if any
    name = request.args.get("name")
    if name:
        # filtering is done on particular shopcart so that we filter this list and not all existing items
        items_found = Item.find_by_name_within_shopcart(shopcart_id, name)
    else:
        items_found = shopcart.items

    # Serialize and return the items in the shopcart
    items = [item.serialize() for item in items_found]
    app.logger.info("Returning %d items", len(items))
    return jsonify(items), status.HTTP_200_OK


######################################################################
# READ AN ITEM FROM A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["GET"])
def get_items(shopcart_id, item_id):  # pylint: disable=unused-argument
    """
    Retrieve a single Item

    This endpoint will return an Item based on it's id
    """
    app.logger.info(
        "Request to Retrieve an item [%s] for Shopcart id: %s", (item_id, shopcart_id)
    )

    # Attempt to find the Item and abort if not found
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    app.logger.info("Returning item: %s", item.name)
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM FROM A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["PUT"])
def update_items(shopcart_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based on the body that is posted
    """
    app.logger.info(
        "Request to update Item %s for Shopcart id: %s", (item_id, shopcart_id)
    )
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    item.deserialize(request.get_json())
    item.id = item_id
    item.update()

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM FROM A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based the id specified in the path
    """
    app.logger.info(
        "Request to Delete an item[%s] for Shopcart id: %s", (item_id, shopcart_id)
    )

    # Attempt to find the Item and delete it if it exists
    item = Item.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# EMPTY A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/empty", methods=["PUT"])
def empty_shopcart(shopcart_id):
    """
    Empty a Shopcart

    This endpoint will remove all items from a Shopcart
    """
    app.logger.info("Request to empty shopcart with id: %s", shopcart_id)

    # Find the shopcart and return 404 if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Clear all items in the shopcart
    shopcart.clear_shopcart()  # This method is implemented in the Shopcart model
    app.logger.info("Shopcart with id [%s] emptied", shopcart_id)

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# MARK AN ITEM AS URGENT
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>/urgent", methods=["PUT"])
def mark_item_urgent(shopcart_id, item_id):
    """
    Mark an item as urgent in a shopcart
    """
    app.logger.info(
        "Request to mark item [%s] as urgent in Shopcart with id: %s",
        item_id,
        shopcart_id,
    )

    # Find the item and return 404 if not found
    item = Item.find(item_id)
    if not item or item.shopcart_id != shopcart_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in shopcart '{shopcart_id}' could not be found.",
        )

    # Mark the item as urgent
    item.is_urgent = True
    item.update()
    app.logger.info("Item [%s] marked as urgent in Shopcart [%s]", item_id, shopcart_id)

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UNMARK AN ITEM AS URGENT
######################################################################
@app.route(
    "/shopcarts/<int:shopcart_id>/items/<int:item_id>/urgent", methods=["DELETE"]
)
def unmark_item_urgent(shopcart_id, item_id):
    """
    Unmark an item as urgent in a shopcart
    """
    app.logger.info(
        "Request to unmark item [%s] as urgent in Shopcart with id: %s",
        item_id,
        shopcart_id,
    )

    # Find the item and return 404 if not found
    item = Item.find(item_id)
    if not item or item.shopcart_id != shopcart_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' in shopcart '{shopcart_id}' could not be found.",
        )

    # Unmark the item as urgent
    item.is_urgent = False
    item.update()
    app.logger.info(
        "Item [%s] unmarked as urgent in Shopcart [%s]", item_id, shopcart_id
    )

    return jsonify(item.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                U  T I L I T Y   F U N C T I O N S
# ---------------------------------------------------------------------


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
