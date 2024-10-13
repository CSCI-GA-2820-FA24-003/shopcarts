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
# cspell:ignore userid
"""
Test cases for Shopcart Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Shopcart, Item, DataValidationError, db
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcart(TestCase):
    """Shopcart Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """It should Create an Shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        # pylint: disable=unexpected-keyword-arg
        shopcart = Shopcart(
            customer_name=fake_shopcart.customer_name,
            created_at=fake_shopcart.created_at,
            last_updated=fake_shopcart.last_updated,
        )
        self.assertIsNotNone(shopcart)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.customer_name, fake_shopcart.customer_name)
        self.assertEqual(shopcart.created_at, fake_shopcart.created_at)
        self.assertEqual(shopcart.last_updated, fake_shopcart.last_updated)

    def test_add_a_shopcart(self):
        """It should Create an shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

    @patch("service.models.db.session.commit")
    def test_add_shopcart_failed(self, exception_mock):
        """It should not create an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.create)

    def test_read_shopcart(self):
        """It should Read an shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Read it back
        found_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.customer_name, shopcart.customer_name)
        self.assertEqual(found_shopcart.created_at, shopcart.created_at)
        self.assertEqual(found_shopcart.last_updated, shopcart.last_updated)
        self.assertEqual(found_shopcart.items, [])

    def test_update_shopcart(self):
        """It should Update an shopcart"""
        shopcart = ShopcartFactory(customer_name="Old Name")
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        self.assertEqual(shopcart.customer_name, "Old Name")

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart.customer_name = "New Name"
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(shopcart.customer_name, "New Name")

    @patch("service.models.db.session.commit")
    def test_update_shopcart_failed(self, exception_mock):
        """It should not update an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.update)

    def test_delete_a_shopcart(self):
        """It should Delete an shopcart from the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_failed(self, exception_mock):
        """It should not delete an Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.delete)

    def test_list_all_shopcarts(self):
        """It should List all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for shopcart in ShopcartFactory.create_batch(5):
            shopcart.create()
        # Assert that there are not 5 shiocarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_find_by_customer_name(self):
        """It should Find an Shopcart by customer name"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Fetch it back by customer name
        same_shopcart = Shopcart.find_by_name(shopcart.customer_name)[0]
        self.assertEqual(same_shopcart.id, shopcart.id)
        self.assertEqual(same_shopcart.customer_name, shopcart.customer_name)

    def test_serialize_a_shopcart(self):
        """It should Serialize a shopcart"""
        shopcart = ShopcartFactory()
        item = ItemFactory()
        shopcart.items.append(item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["customer_name"], shopcart.customer_name)
        self.assertEqual(serial_shopcart["created_at"], shopcart.created_at)
        self.assertEqual(serial_shopcart["last_updated"], shopcart.last_updated)
        self.assertEqual(len(serial_shopcart["items"]), 1)
        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["shopcart_id"], item.shopcart_id)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["description"], item.description)
        self.assertEqual(items[0]["price"], item.price)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["created_at"], item.created_at)
        self.assertEqual(items[0]["last_updated"], item.last_updated)

    def test_deserialize_a_shopcart(self):
        """It should Deserialize a shopcart"""
        shopcart = ShopcartFactory()
        shopcart.items.append(ItemFactory())
        shopcart.create()
        serial_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertEqual(new_shopcart.customer_name, shopcart.customer_name)
        self.assertEqual(new_shopcart.created_at, shopcart.created_at)
        self.assertEqual(new_shopcart.last_updated, shopcart.last_updated)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a shopcart with a KeyError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a shopcart with a TypeError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])


def test_update_shopcart(self):
    """It should Update a shopcart"""
    shopcart = ShopcartFactory(customer_name="Old Name")
    shopcart.create()

    # Update the shopcart
    shopcart.customer_name = "New Name"
    shopcart.update()

    # Fetch it back
    updated_shopcart = Shopcart.find(shopcart.id)
    self.assertEqual(updated_shopcart.customer_name, "New Name")


def test_delete_shopcart(self):
    """It should Delete a shopcart from the database"""
    shopcart = ShopcartFactory()
    shopcart.create()

    # Fetch it back to ensure it exists
    self.assertIsNotNone(Shopcart.find(shopcart.id))

    # Delete the shopcart
    shopcart.delete()

    # Try to fetch it again
    self.assertIsNone(Shopcart.find(shopcart.id))
