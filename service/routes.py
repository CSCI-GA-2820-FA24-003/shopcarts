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
and Delete Shopcarts and Items

Paths:
------
GET / - Displays a UI for Selenium testing
GET /shopcarts - Returns a list all of the Shopcarts
POST /shopcarts - creates a new Shopcart record in the database
GET /shopcarts/{id} - Returns the Shopcart with a given ID number
PUT /shopcarts/{id} - updates a Shopcart record in the database
DELETE /shopcarts/{id} - deletes a Shopcart record in the database
PUT /shopcarts/{id}/empty - empties a Shopcart of items
GET /shopcarts/{id}/items - Returns a list all of the Items in a shopcart
POST /shopcarts/{id}/items - creates a new Item record in the database
GET /shopcarts/{id}/items/{item-id} - Returns the Shopcart with a given id number
PUT /shopcarts/{id}/items/{item-id} - updates an Item record in the database
DELETE /shopcarts/{id}/items/{item-id}- deletes an Item record in the database
PUT /shopcarts/{id}/items/{item-id} - marks Item as urgent
DELETE /shopcarts/{id}/items/{item-id} - marks Item as non-urgent

"""

from flask import jsonify, abort
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
@app.route("/", methods=["GET"])
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
        args = shopcart_args.parse_args()
        if args["customer-name"]:
            app.logger.info("Filtering by customer name: %s", args["customer-name"])
            shopcarts = Shopcart.find_by_customer_name(args["customer-name"])
        else:
            app.logger.info("Returning unfiltered list.")
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
        This endpoint will create a Shopcart based the data in the body
        """
        app.logger.info("Request to Create a Shopcart")
        shopcart = Shopcart()
        app.logger.debug("Payload = %s", api.payload)
        shopcart.deserialize(api.payload)
        shopcart.create()
        app.logger.info("Shopcart with new id [%s] created!", shopcart.id)
        location_url = api.url_for(
            ShopcartResource, shopcart_id=shopcart.id, _external=True
        )
        return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


@api.route("/shopcarts/<int:shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a single Shopcart
    GET /shopcarts/{shopcart_id} - Returns the Shopcart with given id
    PUT /shopcarts/{shopcart_id} - updates a Shopcart record with given id
    DELETE /shopcarts/{shopcart_id} - deletes a Shopcart record with given id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart

        This endpoint will return a Shopcart based on it's id
        """
        app.logger.info("Request to Retrieve a Shopcart with id [%s]", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )
        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING SHOPCART
    # ------------------------------------------------------------------
    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update a Shopcart based the body that is posted
        """
        app.logger.info("Request to Update a shopcart with id [%s]", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        shopcart.deserialize(data)
        shopcart.id = shopcart_id
        shopcart.update()
        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a Shopcart

        This endpoint will delete a Shopcart based the id specified in the path
        """
        app.logger.info("Request to Delete a shopcart with id [%s]", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            shopcart.delete()
            app.logger.info("Shopcart with id [%s] was deleted", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT


@api.route("/shopcarts/<int:shopcart_id>/empty")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartEmptyResource(Resource):
    """
    ShopcartEmptyResource class

    Allows the emptying of a single Shopcart
    PUT /shopcarts/{id}/empty - Empties the Shopcart with given id
    """

    # ------------------------------------------------------------------
    # EMPTY A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("empty_shopcarts")
    @api.response(200, "Shopcart emptied")
    def put(self, shopcart_id):
        """
        Empty a Shopcart

        This endpoint will empty a Shopcart based the id specified in the path
        """
        app.logger.info("Request to Empty a shopcart with id [%s]", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )
        shopcart.clear_shopcart()  # This method is implemented in the Shopcart model
        app.logger.info("Shopcart with id [%s] emptied", shopcart_id)

        return shopcart.serialize(), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items")
@api.param("shopcart_id", "The Shopcart identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Item"""

    @api.doc("list_items")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, shopcart_id):
        """Returns all of the Items within a shopcart"""
        app.logger.info("Request for all items in Shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Process the query string if any
        args = item_args.parse_args()
        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            items_found = Item.find_by_name_within_shopcart(shopcart_id, args["name"])
        else:
            app.logger.info("Returning unfiltered list.")
            items_found = shopcart.items

        items = [item.serialize() for item in items_found]
        app.logger.info("Returning %d items", len(items))
        return items, status.HTTP_200_OK

    @api.doc("create_items")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, shopcart_id):
        """
        Creates a Item
        This endpoint will add an item to a shopcart using payload data
        """
        app.logger.info(
            "Request to create an Item for Shopcart with id: %s", shopcart_id
        )
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' was not found.",
            )

        # Create an item from the json data
        item = Item()
        app.logger.debug("Payload = %s", api.payload)
        item.deserialize(api.payload)
        item.shopcart_id = shopcart_id

        # Append the item to the shopcart
        shopcart.items.append(item)
        shopcart.update()

        app.logger.info(
            "Item with new id [%s] for shopcart_id [%s] created!", item.id, shopcart_id
        )
        location_url = api.url_for(
            ItemResource, shopcart_id=shopcart.id, item_id=item.id, _external=True
        )
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Item
    GET /shopcarts/{shopcart_id}/items/{item_id} - Returns the Shopcart with a given id number
    PUT /shopcarts/{shopcart_id}/items/{item_id} - updates an Item record in the database
    DELETE /shopcarts/{shopcart_id}/items/{item_id} - deletes an Item record in the database
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, shopcart_id, item_id):
        """
        Retrieve a single Item

        This endpoint will return an Item based on the shopcart and item ID
        """
        app.logger.info(
            "Request to Retrieve an Item with id [%s] from shopcart [%s]",
            item_id,
            shopcart_id,
        )
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ITEM
    # ------------------------------------------------------------------
    @api.doc("update_items")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, shopcart_id, item_id):
        """
        Update an Item

        This endpoint will update an Item based the body
        """
        app.logger.info(
            "Request to update Item %s for Shopcart id: %s", item_id, shopcart_id
        )

        # See if the item exists and abort if it doesn't
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )

        # Update from the json in the body of the request
        app.logger.debug("Payload = %s", api.payload)
        item.deserialize(api.payload)
        item.id = item_id
        item.update()
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_items")
    @api.response(204, "Item deleted")
    def delete(self, shopcart_id, item_id):
        """
        Delete an Item

        This endpoint will delete an Item based the id specified in the path
        """
        app.logger.info(
            "Request to Delete an item[%s] for Shopcart id: %s", item_id, shopcart_id
        )

        item = Item.find(item_id)
        if item:
            item.delete()
            app.logger.info(
                "Item[%s] for Shopcart id: %s deleted", item_id, shopcart_id
            )
        return "", status.HTTP_204_NO_CONTENT


@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>/urgent")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemUrgentMarkingResource(Resource):
    """
    ItemUrgentMarkingResource class

    Allows the marking/unmarking of urgent attribute for an Item
    PUT /shopcarts/{shopcart_id}/items/{item_id}/urgent - Marks an item as urgent
    DELETE /shopcarts/{shopcart_id}/items/{item_id}/urgent - Unmarks an item as urgent
    """

    # ------------------------------------------------------------------
    # MARK AN ITEM AS URGENT
    # ------------------------------------------------------------------
    @api.doc("mark_item_urgent")
    @api.response(200, "Item marked urgent")
    def put(self, shopcart_id, item_id):
        """
        Mark an Item Urgent

        This endpoint will mark an item as urgent using given id
        """

        app.logger.info(
            "Request to Mark Urgent an Item with id [%s] from shopcart [%s]",
            item_id,
            shopcart_id,
        )

        # Find the item and return 404 if not found
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )

        # Mark the item as urgent
        item.is_urgent = True
        item.update()
        app.logger.info(
            "Item [%s] marked as urgent in Shopcart [%s]", item_id, shopcart_id
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UNMARK AN ITEM AS URGENT
    # ------------------------------------------------------------------
    @api.doc("unmark_item_urgent")
    @api.response(200, "Item unmarked urgent")
    def delete(self, shopcart_id, item_id):
        """
        Unmark an Item Urgent

        This endpoint will mark an item as urgent using given id
        """

        app.logger.info(
            "Request to Unmark Urgent an Item with id [%s] from shopcart [%s]",
            item_id,
            shopcart_id,
        )

        # Find the item and return 404 if not found
        item = Item.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )

        # Unmark the item as urgent
        item.is_urgent = False
        item.update()
        app.logger.info(
            "Item [%s] unmarked as urgent in Shopcart [%s]", item_id, shopcart_id
        )

        return item.serialize(), status.HTTP_200_OK
