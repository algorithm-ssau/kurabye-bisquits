from sqlalchemy import text

SELECT_ALL_RPODUCT_INFORMATION = text(
    """
    select
	product_id,
	product_name,
	product_price,
	category_id,
	product_image,
	description,
	fats,
	proteins,
	carbohydrates,
	(proteins * 4 + carbohydrates * 4 + fats * 9) as energy,
	grammage,
	jsonb_agg(
		jsonb_build_object(
			'element_id',
			ingredient_id,
			'name',
			ingredient_name,
			'is_allergen',
			is_allergen
		)
	) as composition
    from product
    join md_product using(product_id)
    join product_to_package using(product_id)
    join package using(package_id)
    join product_composition using(product_id)
    join ingredient using(ingredient_id)
    where product_id = :product_id and package_id = :package_id
    group by product_id, description, fats, proteins, carbohydrates, grammage;
    """
)

SELECT_PRODUCTS = text(
    """
    select
        product_id,
        category_id,
        product_image,
        product_name as name,
        product_price as price
    from product
    order by :order_by
    limit :limit
    offset :offset;
    """
)
