from domain.entities.cart import Cart
from schemas.cart import CartItemSchema, CartResponseSchema


def get_cart_schema(cart: Cart) -> CartResponseSchema:
    """
    Get cart items in dict and convert into JSON
    """
    items = {
        item.product_id: CartItemSchema(
            price=item.price,
            product_image=item.product_image,
            grammage=item.grammage,
            name=item.name,
            quantity=quantity,
        )
        for item, quantity in cart.cart_items.items()
    }

    cart_schema = CartResponseSchema(cart_id=cart.cart_id, items=items)

    return cart_schema
