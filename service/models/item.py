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
Item model

Model for storing subordinate Item resources for within a Shopcart
"""
from datetime import datetime
import logging
from .persistent_base import PersistentBase, db, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64))
    description = db.Column(db.String(64))
    price = db.Column(db.Numeric(10, 2, asdecimal=False))
    quantity = db.Column(db.Integer)

    # Database auditing fields
    created_at: datetime = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated: datetime = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] shopcart[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.name}: {self.description}, {self.price}, {self.quantity}"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.name = data["name"]
            self.description = data["description"]
            self.price = data["price"]
            self.quantity = data["quantity"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name_within_shopcart(cls, search_id, name):
        """Returns all Items with the given product name within a shopcart with given id

        Args:
            search_id (int): the shopcart ID of the shopcart you're searching within
            name (string): the name of the Item you want to match
        """
        logger.info(
            "Processing name query for shopcart %d with name %s ...", search_id, name
        )
        return cls.query.filter(cls.shopcart_id == search_id, cls.name == name)
