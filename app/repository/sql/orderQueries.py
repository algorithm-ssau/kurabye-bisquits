from sqlalchemy import text

GET_ORDER = text(
    """
    select
        order_id,
        user_id,
        o.created_at,
        shipping_address,
        status_id,
        order_comment,
        jsonb_agg(product_image) as product_images,
        count(product_id) as product_quantity
    from "order" as o
    join order_item ot using(order_id)
    join lateral(
	select
		product_id,
		product_image
	from product
	where product_id=ot.product_id
	order by product_price
	limit 3
    ) product_images using(product_id)
    where order_id = :order_id
    group by order_id;
    """
)


GET_USER_ORDERS = text(
    """
    select
        order_id,
        user_id,
        shipping_address,
     	order_comment as comment,
        created_at,
	status_id
    from "order"
    where user_id = :user_id;
    """
)

CREATE_ORDER = text(
    """
    insert into "order"(user_id, shipping_address, status_id, order_comment)
    values (:user_id, :shipping_address, :status_id, :order_comment)
    returning order_id;
    """
)

PLACE_CART_ITEMS_TO_ORDER = text(
    """
    with create_order as (
	insert into order_item(order_id, product_id, quantity_of_items, price_per_item)
	(
		select
			:order_id as order_id,
			product_id,
			quantity as quantity_of_items,
			product_price as price_per_item
		from cart_item
		join product using(product_id)
		where cart_id = :user_id
	)
	on conflict(order_id, product_id)
	do update set quantity_of_items = excluded.quantity_of_items + order_item.quantity_of_items
	returning product_id
    )
    delete from cart_item where (product_id, :user_id) in (select product_id, cart_id from create_order);

    """
)

CLEAR_INVENTORY = text(
    """
    WITH quantity_order AS
    (
        SELECT
            quantity_of_items,
            product_id
        FROM order_item
        WHERE order_id = :order_id
    )
    UPDATE inventory i
    SET stock_quantity = stock_quantity - qo.quantity_of_items
    FROM quantity_order qo
    WHERE i.product_id = qo.product_id;
    """
)

GET_ORDER = text(
    """
    select
        o.order_id,
        o.created_at,
        o.user_id,
        o.shipping_address,
        os.status_name,
        os.status_id,
        o.order_comment,
	jsonb_agg(
		jsonb_build_object(
			'product_id',
			p.product_id,
			'product_name',
			p.product_name,
			'product_price',
			oi.price_per_item,
			'quantity_in_order',
			oi.quantity_of_items
		)
	) as product_list
    from "order" o
    join order_item oi using(order_id)
    join product p using(product_id)
    join order_status os using(status_id)
    where o.order_id = :order_id
    group by o.order_id, os.status_name, os.status_id;
    """
)

GET_ALL_ORDERS = text(
    """
    select
        o.order_id,
        o.created_at,
        o.user_id,
        o.shipping_address,
        os.status_name,
        os.status_id,
        o.order_comment as comment,
        jsonb_agg(
            jsonb_build_object(
                'product_id',
                p.product_id,
                'product_name',
                p.product_name,
                'product_price',
                oi.price_per_item,
                'quantity_in_order',
                oi.quantity_of_items
            )
        )
    from "order" o
    join order_item oi using(order_id)
    join product p using(product_id)
    join order_status os using(status_id)
    where os.status_id != :excepted_status_id
    group by o.order_id, os.status_name, os.status_id;
    """
)


# this query will transfer the order_items and the order in the corresponding deleted_tables.
# In another words it will be safe delete. But order status will delete PERMAMENTLY (now the business logic
# doesn't need the status history of the deleted orders).
SAFE_DELETE_ORDER = text(
    """
    with deleting_order_item as (
	delete from order_item where order_id = :order_id
	returning *
    )

    insert into deleted_order_item (select * from deleting_order_item);
    delete from order_status_history where order_id = :order_id;

    with deleting_order as (
	delete from "order" where order_id = :order_id
	returning *
    )
    insert into deleted_order (select * from deleting_order);

    """
)


UPDATE_ORDER_STATUS = text(
    """
    update "order" set status_id = :status_id where order_id = :order_id;
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
