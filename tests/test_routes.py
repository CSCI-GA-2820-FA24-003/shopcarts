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


import unittest
from unittest.mock import patch
from service import app
from flask import json


class TestErrorHandlers(unittest.TestCase):

    def setUp(self):
        """Runs before each test"""
        self.app = app.test_client()
        self.app.testing = True

    def test_bad_request_error(self):
        """It should return 400 for bad requests"""
        response = self.app.post(
            "/shopcarts",
            json={},  # 传入无效的空数据，导致数据验证错误
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_not_found_error(self):
        """It should return 404 for a non-existing resource"""
        response = self.app.get("/shopcarts/0")  # 试图获取不存在的shopcart
        self.assertEqual(response.status_code, 404)

    def test_method_not_allowed_error(self):
        """It should return 405 when using an unsupported method"""
        response = self.app.put("/shopcarts", json={})
        self.assertEqual(response.status_code, 405)

    def test_unsupported_media_type_error(self):
        """It should return 415 for unsupported media types"""
        response = self.app.post(
            "/shopcarts",
            data="invalid data",  # 发送不支持的数据类型
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 415)

    @patch("service.models.Shopcart.find")
    def test_internal_server_error(self, mock_find):
        """It should return 500 for internal server error"""
        mock_find.side_effect = Exception("Database error")  # 模拟一个服务器内部错误
        response = self.app.get("/shopcarts/1")
        self.assertEqual(response.status_code, 500)


def test_bad_request_error(self):
    """It should return 400 for bad requests"""
    response = self.client.post(
        "/shopcarts",
        json={},  # 传入无效的空数据，导致数据验证错误
        content_type="application/json",
    )
    self.assertEqual(response.status_code, 400)


def test_not_found_error(self):
    """It should return 404 for a non-existing resource"""
    response = self.client.get("/shopcarts/0")  # 试图获取不存在的 shopcart
    self.assertEqual(response.status_code, 404)


def test_method_not_allowed_error(self):
    """It should return 405 when using an unsupported method"""
    response = self.client.put("/shopcarts", json={})
    self.assertEqual(response.status_code, 405)


def test_unsupported_media_type_error(self):
    """It should return 415 for unsupported media types"""
    response = self.client.post(
        "/shopcarts",
        data="invalid data",  # 发送不支持的数据类型
        content_type="text/plain",
    )
    self.assertEqual(response.status_code, 415)


@patch("service.models.Shopcart.find")
def test_internal_server_error(self, mock_find):
    """It should return 500 for internal server error"""
    mock_find.side_effect = Exception("Database error")  # 模拟一个服务器内部错误
    response = self.client.get("/shopcarts/1")
    self.assertEqual(response.status_code, 500)


def test_root_url(self):
    """It should return useful information at the root URL"""
    response = self.client.get("/")
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Check if the response contains name, version, and list_resource_url
    data = response.get_json()
    self.assertIn("name", data)
    self.assertIn("version", data)
    self.assertIn("list_resource_url", data)

    # Optional: You can check the exact values if needed
    self.assertEqual(data["name"], "Shopcart API Service")
    self.assertEqual(data["version"], "1.0.0")
    self.assertEqual(data["list_resource_url"], "/shopcarts")
