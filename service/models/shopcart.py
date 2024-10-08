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
# cspell: ignore= userid, backref
"""
Shopcart model

Model for storing overall shopcart resource
"""

import logging
from .persistent_base import PersistentBase, db, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")


######################################################################
#  S H O P C A R T  M O D E L
######################################################################
class Shopcart(db.Model, PersistentBase):
    """
    Class that represents an Shopcart
    """

    # Table Schema

    # id matches to customer ID since is only one shopcart per customer
    id = db.Column(db.Integer, primary_key=True)
    # name for ease of matching/auditing
    customer_name = db.Column(db.String(64), nullable=False)
    items = db.relationship("Item", backref="shopcart", passive_deletes=True)

    # Database auditing fields
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Shopcart {self.customer_name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Shopcart into a dictionary"""
        shopcart = {
            "id": self.id,
            "customer_name": self.customer_name,
            "items": [],
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates an Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            # self.id = data["id"] do we need this
            self.customer_name = data["customer_name"]
            self.created_at = data["created_at"]
            self.last_updated = data["last_updated"]

            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, customer_name):
        """Returns all Shopcarts with the given customer name

        Args:
            customer_name (string): the customer_name of the Shopcarts you want to match
        """
        logger.info("Processing name query for %s ...", customer_name)
        return cls.query.filter(cls.customer_name == customer_name)
