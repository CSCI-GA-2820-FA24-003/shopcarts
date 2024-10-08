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
from datetime import datetime
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

        # Todo: uncomment this code when get_shopcarts is implemented
        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_shopcart = response.get_json()
        # self.assertEqual(new_shopcart["customer_name"], test_shopcart.customer_name)
        # self.assertEqual(new_shopcart["items"], test_shopcart.items)

        # # Convert the string date to a datetime object
        # created_at_date = datetime.strptime(
        #     new_shopcart["created_at"], "%a, %d %b %Y %H:%M:%S %Z"
        # ).date()
        # last_updated_date = datetime.strptime(
        #     new_shopcart["last_updated"], "%a, %d %b %Y %H:%M:%S %Z"
        # ).date()
        # # Compare the parsed date with `test_shopcart.created_at`
        # self.assertEqual(created_at_date, test_shopcart.created_at)
        # self.assertEqual(last_updated_date, test_shopcart.last_updated)
