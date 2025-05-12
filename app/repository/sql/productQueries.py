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
    left join product_composition using(product_id)
    left join ingredient using(ingredient_id)
    where product_id = :product_id
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
    	product_price as price,
        grammage
    from product
    join inventory using(product_id)
    group by product_id
    having sum(stock_quantity) > 0
    order by product.product_name
    limit :limit
    offset :offset;
    """
)

# update with locking
UPDATE_PRODUCT = text(
    """
    select
	product_id
    from product
    join md_product using (product_id)
    where product_id = :product_id
    for update;

    update product set
	category_id = :category_id,
	product_image = :product_image,
	product_name = :product_name,
	product_price = :product_price,
	updated_at = current_timestamp
    where product_id = :product_id;

    update md_product set
	description = :description,
	fats = :fats,
	proteins = :proteins,
	carbohydrates = :carbohydrates
    where product_id = :product_id
    """
)
