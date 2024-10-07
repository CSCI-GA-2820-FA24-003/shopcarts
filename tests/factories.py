"""
Test Factory to make fake objects for testing
"""

from datetime import date
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyDecimal, FuzzyInteger
from service.models import Shopcart, Item


class ShopcartFactory(Factory):
    """Creates fake Shopcarts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Shopcart

    id = Sequence(lambda n: n)
    customer_name = Faker("name")
    created_at = FuzzyDate(date(2008, 1, 1))
    last_updated = FuzzyDate(date(2008, 1, 1))
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = Sequence(lambda n: n)
    shopcart_id = None
    name = FuzzyChoice(choices=["shirt", "pant", "hat"])
    description = FuzzyChoice(
        choices=["a shirt to wear", "a pant to wear", "a hat to wear"]
    )
    price = FuzzyDecimal(0.1, 20.0)
    quantity = FuzzyInteger(1, 30)
    created_at = FuzzyDate(date(2008, 1, 1))
    last_updated = FuzzyDate(date(2008, 1, 1))
    shopcart = SubFactory(ShopcartFactory)
