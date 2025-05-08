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
    join product_to_package using(product_id)
    join package using(package_id)
    where cart_id = :cart_id
    group by cart_id;
    """
)
