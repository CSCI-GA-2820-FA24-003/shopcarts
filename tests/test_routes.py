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

from service.common import status
from service.models import Shopcart, db
from wsgi import app

from .factories import ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"


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
    def _create_shopcarts(self, count: int = 1) -> list:
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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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

        # Convert the string date to a datetime object
        created_at_date = datetime.strptime(
            new_shopcart["created_at"], "%a, %d %b %Y %H:%M:%S %Z"
        ).date()
        last_updated_date = datetime.strptime(
            new_shopcart["last_updated"], "%a, %d %b %Y %H:%M:%S %Z"
        ).date()
        # Compare the parsed date with `test_shopcart.created_at`
        self.assertEqual(created_at_date, test_shopcart.created_at)
        self.assertEqual(last_updated_date, test_shopcart.last_updated)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_name"], test_shopcart.customer_name)
        self.assertEqual(new_shopcart["items"], test_shopcart.items)

        # Convert the string date to a datetime object
        created_at_date = datetime.strptime(
            new_shopcart["created_at"], "%a, %d %b %Y %H:%M:%S %Z"
        ).date()
        last_updated_date = datetime.strptime(
            new_shopcart["last_updated"], "%a, %d %b %Y %H:%M:%S %Z"
        ).date()
        # Compare the parsed date with `test_shopcart.created_at`
        self.assertEqual(created_at_date, test_shopcart.created_at)
        self.assertEqual(last_updated_date, test_shopcart.last_updated)

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
        new_account_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_account_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_account = resp.get_json()
        self.assertEqual(updated_account["customer_name"], "New name")
        self.assertGreater(
            datetime.fromisoformat(updated_account["last_updated"]).replace(tzinfo=UTC),
            old_updated_time,
        )

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
        self.assertIn("Shopcart with id '0' could not be found.", data["message"])

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
