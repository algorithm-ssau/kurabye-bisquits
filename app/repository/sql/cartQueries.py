from sqlalchemy import text

SELECT_CART_ITEMS = text(
    """
    select
	cart_id,
	jsonb_agg(
		jsonb_build_object(
			'product_id',
			product_id,
			'grammage',
			grammage,
			'category_id',
			category_id,
			'product_image',
			product_image,
			'name',
			product_name,
			'price',
			product_price,
			'quantity',
			quantity
		)
	) as products
    from cart
    join cart_item using(cart_id)
    join product using(product_id)
    where cart_id = :cart_id
    group by cart_id;
    """
)

UPSERT_PRODUCT_IN_CART = text(
    """
    insert into cart_item (cart_id, product_id, quantity)
    values (:cart_id, :product_id, :quantity)
    on conflict (cart_id, product_id)
    do update set quantity = cart_item.quantity + excluded.quantity
    returning quantity;
    """
)


DELETE_QUANTITY_OF_PRODUCT = text(
    """
    update cart_item set quantity = cart_item.quantity - :quantity_to_delete
    where cart_id = :cart_id and product_id = :product_id;
    """
)

DELETE_ALL_PRODUCTS = text(
    """
    delete from cart_item where cart_id = :cart_id and product_id = :product_id;
    """
)

CREATE_CART = text(
    """
    insert into cart(cart_id) values(:cart_id)
    on conflict(cart_id) do nothing;
    """
)


GET_TOTAL_PRODUCT_QUANTITY = text(
    """
    select
    	sum(stock_quantity) as total_quantity
    from inventory
    where product_id = :product_id
    group by product_id;
    """
)
