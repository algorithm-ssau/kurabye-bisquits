from collections import defaultdict

from pydantic import BaseModel

from domain.entities.product import Product


class Cart(BaseModel):
    cart_id: int  # cart_id alias of user_id. Cart is the data, that expands user data.
    items: defaultdict[Product, int] = defaultdict(int)

    def __contains__(self, item):
        return item in self.items
