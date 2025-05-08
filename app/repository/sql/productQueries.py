from sqlalchemy import text

SELECT_ALL_RPODUCT_INFORMATION = text(
    """
    select
        product_id,
        category_id,
        product_image,
        description,
        fats,
        proteis,
        carbonydrates
    from product
    join md_product using(product_id)
    where product_id = :product_id
    """
)
