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
TestShopcart API Service Test Suite
"""

import logging

# pylint: disable=duplicate-code
import os
from datetime import UTC, datetime
from unittest import TestCase
from urllib.parse import quote_plus

from service.common import status
from service.models import Shopcart, db
from wsgi import app

from .factories import ItemFactory, ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/api/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcart(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create shopcarts
    ############################################################
    def _create_shopcarts(self, count: int = 1) -> list[Shopcart]:
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    ############################################################
    # Utility function to create items in shopcarts
    ############################################################

    def _create_items(self, shopcart_id, number_of_items):
        """Helper method to create items for a shopcart"""
        items = []
        for _ in range(number_of_items):
            test_item = (
                ItemFactory()
            )  # Assuming you have ItemFactory to generate item instances
            response = self.client.post(
                f"{BASE_URL}/{shopcart_id}/items",
                json=test_item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test item",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.content_type, "text/html; charset=utf-8")

    def test_health_check(self):
        """It should call the health check endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "Healthy")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_shopcart(self):
        """It should Create a new Shopcart"""
        test_shopcart = ShopcartFactory()
        logging.debug("Test Shopcart: %s", test_shopcart.serialize())
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_name"], test_shopcart.customer_name)
        self.assertEqual(new_shopcart["items"], test_shopcart.items)

        # Make sure server assigned a created/updated date
        # (this will overwrite the ones from factory)
        self.assertIsNotNone(test_shopcart.created_at)
        self.assertIsNotNone(test_shopcart.last_updated)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_name"], test_shopcart.customer_name)
        self.assertEqual(new_shopcart["items"], test_shopcart.items)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_shopcart(self):
        """It should Update an existing Shopcart"""
        # create an Shopcart to update
        test_shopcart = ShopcartFactory()
        resp = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        old_updated_time = test_shopcart.last_updated
        new_shopcart["customer_name"] = "New name"
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["customer_name"], "New name")
        self.assertGreater(
            datetime.fromisoformat(updated_shopcart["last_updated"]).replace(
                tzinfo=UTC
            ),
            old_updated_time,
        )

    def test_delete_shopcart(self):
        """It should Delete a Shopcart"""
        # get the id of a shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existing_shopcart(self):
        """It should Delete a Shopcart even if it doesn't exist"""
        # Attempt to delete a non-existing shopcart
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart_list_filtered(self):
        """It should Get a list of Shopcarts with a customer name filter"""
        test_shopcarts = self._create_shopcarts(5)
        filtered_name = test_shopcarts[0].customer_name
        response = self.client.get(
            BASE_URL, query_string={"customer-name": filtered_name}
        )
        filtered_amount = len(
            [x for x in test_shopcarts if x.customer_name == filtered_name]
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), filtered_amount)

    def test_get_shopcart(self):
        """It should get a single Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_shopcart.id)

    def test_get_shopcart_when_shopcart_not_found(self):
        """It should not get a Shopcart that's not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("Shopcart with id '0' was not found.", data["message"])

    # ----------------------------------------------------------
    # IMPROPER REQUEST TESTS
    # ----------------------------------------------------------
    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  I T E M   T E S T   C A S E S
    ######################################################################

    def test_add_item(self):
        """It should Add an item to a shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["quantity"], item.quantity)

        # Make sure server assigned a created/updated date
        # (this will overwrite the ones from factory)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.last_updated)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["name"], item.name, "Item name does not match")

    def test_list_all_items_in_shopcart(self):
        """It should return a list of all Items in a Shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 2)

        # List all items
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_list_all_items_filtered(self):
        """It should return a list of all Items in a Shopcart after filtering for a name"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        test_items = self._create_items(shopcart.id, 2)
        filtered_name = test_items[0].name

        # List all items
        response = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items",
            query_string=f"name={quote_plus(filtered_name)}",
        )
        filtered_amount = len([x for x in test_items if x.name == filtered_name])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), filtered_amount)

    def test_list_all_items_in_shopcart_when_shopcart_not_found(self):
        """It should not list all Items in a Shopcart that's not found"""
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            "Shopcart with id '0' was not found.",
            resp.get_json()["message"],
        )

    def test_get_item(self):
        """It should Get a single Item from a shopcart"""
        # Create a shopcart and add an item to it
        shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(shopcart.id, 1)[0]

        # Retrieve the item by its ID
        item_id = test_item.id
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the item data matches the created item
        data = response.get_json()
        self.assertEqual(data["name"], test_item.name)

    def test_get_item_not_found(self):
        """It should not Get an Item thats not found"""
        # Create a shopcart but do not add items
        shopcart = self._create_shopcarts(1)[0]

        # Try to retrieve a non-existent item (using ID 0)
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check that the error message is correct
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_update_item(self):
        """It should Update an item in a shopcart"""
        # create a known item
        shopcart = self._create_shopcarts(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        old_updated_time = item.last_updated
        item_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_item = resp.get_json()

        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["shopcart_id"], shopcart.id)
        self.assertEqual(data["name"], "XXXX")
        self.assertGreater(
            datetime.fromisoformat(updated_item["last_updated"]).replace(tzinfo=UTC),
            old_updated_time,
        )

    def test_delete_item(self):
        """It should Delete an Item"""
        # Create a shopcart and add an item to it
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(test_shopcart.id, 1)[0]

        # Delete the item
        response = self.client.delete(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # Verify the item is actually deleted
        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_item(self):
        """It should Delete an Item even if it doesn't exist"""
        # Create a shopcart without items
        shopcart = self._create_shopcarts(1)[0]

        # Attempt to delete a non-existing item
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST EMPTY SHOPCART
    # ----------------------------------------------------------
    def test_empty_shopcart(self):
        """It should empty a shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 3)  # Add 3 items to the shopcart

        # Verify the shopcart has items
        response = self.client.get(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreater(
            len(data["items"]), 0, "Shopcart should initially have items"
        )

        # Call the empty endpoint
        response = self.client.put(f"{BASE_URL}/{shopcart.id}/empty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the shopcart is now empty
        data = response.get_json()
        self.assertEqual(
            len(data["items"]), 0, "Shopcart should be empty after emptying"
        )

    def test_empty_shopcart_idempotent(self):
        """It should be idempotent when emptying a shopcart"""
        # Create a shopcart with items and empty it
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 3)
        self.client.put(f"{BASE_URL}/{shopcart.id}/empty")

        # Verify the shopcart is empty
        response = self.client.put(f"{BASE_URL}/{shopcart.id}/empty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that calling empty again does not change the result
        data = response.get_json()
        self.assertEqual(
            len(data["items"]), 0, "Shopcart should remain empty on repeated calls"
        )

    def test_empty_shopcart_not_found(self):
        """It should not empty a Shopcart that's not found"""
        response = self.client.put(f"{BASE_URL}/0/empty")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("Shopcart with id '0' was not found.", data["message"])

        # ----------------------------------------------------------

    # TEST MARK ITEM AS URGENT
    # ----------------------------------------------------------
    def test_mark_item_as_urgent(self):
        """It should mark an item as urgent"""
        # Create a shopcart and add an item
        shopcart = self._create_shopcarts(1)[0]
        item = self._create_items(shopcart.id, 1)[0]

        # Mark the item as urgent
        response = self.client.put(f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the item is marked as urgent
        data = response.get_json()
        self.assertTrue(data["is_urgent"], "Item should be marked as urgent")

    # ----------------------------------------------------------
    # TEST UNMARK ITEM AS URGENT
    # ----------------------------------------------------------
    def test_unmark_item_as_urgent(self):
        """It should unmark an item as urgent"""
        # Create a shopcart and add an urgent item
        shopcart = self._create_shopcarts(1)[0]
        item = self._create_items(shopcart.id, 1)[0]

        # Mark the item as urgent first
        self.client.put(f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent")

        # Unmark the item as urgent
        response = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the item is unmarked as urgent
        data = response.get_json()
        self.assertFalse(data["is_urgent"], "Item should be unmarked as urgent")

    # ----------------------------------------------------------
    # TEST IDPOTENT MARK/UNMARK AS URGENT
    # ----------------------------------------------------------
    def test_idempotent_mark_unmark_as_urgent(self):
        """It should be idempotent for marking and unmarking urgent"""
        # Create a shopcart and add an item
        shopcart = self._create_shopcarts(1)[0]
        item = self._create_items(shopcart.id, 1)[0]

        # Mark the item as urgent twice
        self.client.put(f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent")
        response = self.client.put(f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(data["is_urgent"], "Item should stay marked as urgent")

        # Unmark the item as urgent twice
        self.client.delete(f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent")
        response = self.client.delete(
            f"{BASE_URL}/{shopcart.id}/items/{item.id}/urgent"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertFalse(data["is_urgent"], "Item should stay unmarked as urgent")
