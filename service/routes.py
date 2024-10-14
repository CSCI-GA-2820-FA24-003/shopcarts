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

from datetime import datetime
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart, Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for shopcart list")

    shopcarts = []

    shopcarts = Shopcart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Create a Shopcart
    This endpoint will create a Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to Create a Shopcart...")
    check_content_type("application/json")

    shopcart = Shopcart()
    # Get the data from the request and deserialize it
    data = request.get_json()
    # Make sure to fill in the audit dates and start with an empty item list
    data["items"] = []

    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)
    shopcart.created_at = datetime.now()
    shopcart.last_updated = datetime.now()

    # Save the new Shopcart to the database
    shopcart.create()
    app.logger.info("Shopcart with new id [%s] saved!", shopcart.id)

    # Return the location of the new Shopcart
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


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

    # See if the account exists and abort if it doesn't
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
    if "items" not in updated_json:
        updated_json["items"] = shopcart.serialize()["items"]
    shopcart.deserialize(updated_json)
    shopcart.id = shopcart_id
    shopcart.last_updated = datetime.now()
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
    item.created_at = datetime.now()
    item.last_updated = datetime.now()
    shopcart.last_updated = datetime.now()

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

    # Serialize and return the items in the shopcart
    items = [item.serialize() for item in shopcart.items]
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
    app.logger.info("Request to Retrieve an item with id [%s]", item_id)

    # Find the shopcart first
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Find the item within the specified shopcart
    item = next((item for item in shopcart.items if item.id == item_id), None)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found in shopcart '{shopcart_id}'.",
        )

    app.logger.info("Returning item: %s", item.name)
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
    app.logger.info("Request to Delete an item with id [%s]", item_id)

    # Find the shopcart first
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    # Delete the Item if it exists
    item = Item.find(item_id)
    if item:
        app.logger.info("Item with ID: %d found.", item.id)
        item.delete()

    app.logger.info("Item with ID: %d delete complete.", item_id)
    return {}, status.HTTP_204_NO_CONTENT


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
