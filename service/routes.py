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
from service.models import Shopcart
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
    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)

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
    Retrieve a single Account

    This endpoint will return an Account based on it's id
    """
    app.logger.info("Request for Account with id: %s", shopcart_id)

    # See if the account exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to shopcart account with id: %s", shopcart_id)
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
