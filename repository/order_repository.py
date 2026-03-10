import json
from datetime import datetime
from typing import List, Optional
from model.item_in_order_response import ItemInOrderResponse
from model.item_response import ItemResponse
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_summary import OrderSummary
from model.user_response import UserResponse
from repository import cache_repository
from repository.database import database
TABLE_NAME = "orders"
all_cache_key = "all_orders"



## Returns an order by id
async def get_by_id(order_id: int) -> Optional[OrderResponse]:

    cache_key=f"order_{order_id}"
    if cache_repository.is_key_exists(cache_key):
        order_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return OrderResponse(**order_dict)



    query_order = """
            SELECT 
                orders.id AS order_id,
                orders.buyer_id,
                orders.order_status,
                orders.order_date,
                orders.order_address,
                users.id AS user_id,
                users.first_name,
                users.last_name,
                users.email,
                users.phone,
                users.address AS user_address,
                users.user_name
            FROM orders
            JOIN users ON orders.buyer_id = users.id
            WHERE orders.id = :order_id;
        """
    order_row = await database.fetch_one(query_order, values={"order_id": order_id})

    if not order_row:
        return None

    query_items = """
            SELECT 
                item.id,
                item.item_name,
                item.price,
                item.amount_in_stock,
                item.image_url,
                item_in_order.amount_in_order,
                item_in_order.id AS iio_id
            FROM item_in_order
            JOIN item ON item_in_order.item_id = item.id
            WHERE item_in_order.order_id = :order_id;
        """
    item_rows = await database.fetch_all(query_items, values={"order_id": order_id})

    order_items = []
    total_price = 0.0
    total_amount = 0

    for row in item_rows:
        item_instance = ItemResponse(
            id=row["id"],
            item_name=row["item_name"],
            price=row["price"],
            amount_in_stock=int(row["amount_in_stock"]),
            image_url=row["image_url"] or ""
        )

        item_total = float(row["price"]) * row["amount_in_order"]

        order_item_instance = ItemInOrderResponse(
            id=int(row["iio_id"]),
            item=item_instance,
            amount_in_order=row["amount_in_order"],
            total_price=item_total,
            order_id=order_id
        )

        order_items.append(order_item_instance)
        total_price += item_total
        total_amount += row["amount_in_order"]

    customer_instance = UserResponse(
        id=order_row["buyer_id"],
        first_name=order_row["first_name"],
        last_name=order_row["last_name"],
        email=order_row["email"],
        phone=order_row["phone"],
        address=order_row["user_address"],
        user_name=order_row["user_name"]
    )

    order= OrderResponse(
        id=order_row["order_id"],
        order_status=order_row["order_status"],
        customer=customer_instance,
        order_date=order_row["order_date"],
        order_address=order_row["order_address"],
        total_price=total_price,
        order_items=order_items,
        item_amount=total_amount)

    order_json = order.model_dump_json()
    cache_repository.create_cache_entity(cache_key, order_json)

    return order




async def get_order_id_by_user_id(buyer_id: int):
    query = f"SELECT id FROM {TABLE_NAME} WHERE buyer_id = :buyer_id"
    rows = await database.fetch_all(query, {"buyer_id": buyer_id})
    return rows


async def get_buyer_id_by_order_id(order_id: int):
    query = f"SELECT buyer_id FROM {TABLE_NAME} WHERE id=:order_id"
    row = await database.fetch_one(query, {"order_id": order_id})
    if not row:
        return None
    return int(row["buyer_id"])


async def get_all() -> List[OrderResponse]:
    if cache_repository.is_key_exists(all_cache_key):
        orders_dict = json.loads(cache_repository.get_cache_entity(all_cache_key))
        return [OrderResponse(**order) for order in orders_dict]

    query_orders = f"""
        SELECT 
            orders.id AS order_id,
            orders.buyer_id,
            orders.order_status,
            orders.order_date,
            orders.order_address,
            users.id AS user_id,
            users.first_name,
            users.last_name,
            users.email,
            users.phone,
            users.address AS user_address,
            users.user_name
        FROM {TABLE_NAME}
        JOIN users ON orders.buyer_id = users.id;
    """

    orders_rows = await database.fetch_all(query_orders)
    all_orders = []

    for order_row in orders_rows:

        query_items = """
            SELECT 
                item.id AS item_id,
                item.item_name,
                item.price,
                item.amount_in_stock,
                item.image_url,
                item_in_order.amount_in_order,
                item_in_order.order_id,
                item_in_order.id AS iio_id
            FROM item_in_order
            JOIN item ON item_in_order.item_id = item.id
            WHERE item_in_order.order_id = :order_id;
        """

        item_rows = await database.fetch_all(
            query_items,
            values={"order_id": order_row["order_id"]}
        )

        order_items = []
        total_price = 0.0
        total_amount = 0

        for row in item_rows:
            item_instance = ItemResponse(
                id=int(row["item_id"]),
                item_name=row["item_name"],
                price=float(row["price"]),
                amount_in_stock=int(row["amount_in_stock"]),
                image_url=row["image_url"] or "https://katzr.net/a0cf43"
            )

            order_item_instance = ItemInOrderResponse(
                id=int(row["iio_id"]),
                item=item_instance,
                amount_in_order=int(row["amount_in_order"]),
                total_price=float(row["price"]) * int(row["amount_in_order"]),
                order_id=int(row["order_id"])
            )

            order_items.append(order_item_instance)

            total_price += order_item_instance.total_price
            total_amount += int(row["amount_in_order"])

        customer_instance = UserResponse(
            id=int(order_row["user_id"]),
            first_name=order_row["first_name"],
            last_name=order_row["last_name"],
            email=order_row["email"],
            phone=order_row["phone"],
            address=order_row["user_address"],
            user_name=order_row["user_name"]
        )

        all_orders.append(
            OrderResponse(
                id=int(order_row["order_id"]),
                order_status=order_row["order_status"],
                customer=customer_instance,
                order_date=order_row["order_date"],
                order_address=order_row["order_address"],
                total_price=total_price,
                order_items=order_items,
                item_amount=total_amount
            )
        )
    orders_json = json.dumps([order.model_dump() for order in all_orders])
    cache_repository.create_cache_entity(all_cache_key, orders_json)
    return all_orders


## Returns all orders by user id
async def get_all_by_user(buyer_id: int) -> List[OrderResponse]:

    users_order_cache_key = f"orders_user_{buyer_id}"
    if cache_repository.is_key_exists(users_order_cache_key):
        orders_dict = json.loads(cache_repository.get_cache_entity(users_order_cache_key))
        return [OrderResponse(**order) for order in orders_dict]

    query_orders = f"""
        SELECT 
            orders.id AS order_id,
            orders.buyer_id,
            orders.order_status,
            orders.order_date,
            orders.order_address,
            users.id AS user_id,
            users.first_name,
            users.last_name,
            users.email,
            users.phone,
            users.address AS user_address,
            users.user_name
        FROM {TABLE_NAME}
        JOIN users ON orders.buyer_id = users.id
        WHERE orders.buyer_id = :buyer_id
    """

    orders_rows = await database.fetch_all(query_orders, values={"buyer_id": buyer_id})
    all_orders = []

    for order_row in orders_rows:

        query_items = """
            SELECT 
                item.id AS item_id,
                item.item_name,
                item.price,
                item.amount_in_stock,
                item.image_url,
                item_in_order.amount_in_order,
                item_in_order.order_id,
                item_in_order.id AS iio_id
            FROM item_in_order
            JOIN item ON item_in_order.item_id = item.id
            WHERE item_in_order.order_id = :order_id;
        """

        item_rows = await database.fetch_all(
            query_items,
            values={"order_id": order_row["order_id"]}
        )

        order_items = []
        total_price = 0.0
        total_amount = 0

        for row in item_rows:
            item_instance = ItemResponse(
                id=int(row["item_id"]),
                item_name=row["item_name"],
                price=float(row["price"]),
                amount_in_stock=int(row["amount_in_stock"]),
                image_url=row["image_url"] or "https://katzr.net/a0cf43"
            )

            order_item_instance = ItemInOrderResponse(
                id=int(row["iio_id"]),
                item=item_instance,
                amount_in_order=int(row["amount_in_order"]),
                total_price=float(row["price"]) * int(row["amount_in_order"]),
                order_id=int(row["order_id"])
            )

            order_items.append(order_item_instance)

            total_price += order_item_instance.total_price
            total_amount += int(row["amount_in_order"])

        customer_instance = UserResponse(
            id=int(order_row["user_id"]),
            first_name=order_row["first_name"],
            last_name=order_row["last_name"],
            email=order_row["email"],
            phone=order_row["phone"],
            address=order_row["user_address"],
            user_name=order_row["user_name"]
        )

        all_orders.append(
            OrderResponse(
                id=int(order_row["order_id"]),
                order_status=order_row["order_status"],
                customer=customer_instance,
                order_date=order_row["order_date"],
                order_address=order_row["order_address"],
                total_price=total_price,
                order_items=order_items,
                item_amount=total_amount
            )
        )
        orders_json = json.dumps([order.model_dump() for order in all_orders])
        cache_repository.create_cache_entity(users_order_cache_key, orders_json)

    return all_orders


async def get_all_id_by_user(buyer_id: int) -> List[int]:
    query_orders = f"SELECT id FROM {TABLE_NAME} WHERE buyer_id = :buyer_id;"
    values = {"buyer_id": buyer_id}
    rows = await database.fetch_all(query_orders, values)
    return [row["id"] for row in rows]



## Creates a new order
async def create_order(new_order: OrderRequest) -> int:
    query = f"""
    INSERT INTO {TABLE_NAME} (buyer_id, order_date, order_address, order_status)
    VALUES (:buyer_id,:order_date, :order_address, :order_status)
    """
    values = {
        "buyer_id": new_order.buyer_id,
        "order_date": new_order.order_date,
        "order_address": new_order.order_address,
        "order_status": new_order.order_status.value
    }

    last_record_id = await database.execute(query, values)
    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(f"user_order_{new_order.buyer_id}")

    return last_record_id


## Updates an existing order
async def update_order(order_id: int, updated_order: OrderRequest) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET buyer_id = :buyer_id,
        order_date= :order_date,
        order_address = :order_address,
        order_status = :order_status
    WHERE id = :order_id
    """
    values = {
        "buyer_id": updated_order.buyer_id,
        "order_date": updated_order.order_date,
        "order_address": updated_order.order_address,
        "order_status": updated_order.order_status.value,
        "order_id": order_id,
    }

    async with database.transaction():
        result = await database.execute(query, values)

    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(f"order_{order_id}")
    cache_repository.remove_cache_entity(f"user_order_{updated_order.buyer_id}")
    cache_repository.remove_cache_entity(f"temp_{updated_order.buyer_id}")

    return result


## Deletes a specific order
async def delete_order(order_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id = :order_id"
    values = {"order_id": order_id}

    buyer_id= await get_buyer_id_by_order_id(order_id)
    cache_repository.remove_cache_entity(f"user_order_{buyer_id}")
    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(f"order_{order_id}")
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")


    await database.execute(query, values)
    return order_id


async def delete_orders_for_user(buyer_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE buyer_id = :buyer_id"
    values = {"buyer_id": buyer_id}

    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(f"user_order_{buyer_id}")
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")
    ids=await get_order_id_by_user_id(buyer_id)
    for id in ids:
        cache_repository.remove_cache_entity(f"order_{id}")

    await database.execute(query, values)


async def get_temp_order_by_user(buyer_id: int) -> Optional[OrderResponse]:
    temp_order_cache_key = f"temp_{buyer_id}"
    if cache_repository.is_key_exists(temp_order_cache_key):
        temp_dict = json.loads(cache_repository.get_cache_entity(temp_order_cache_key))
        return OrderResponse(**temp_dict)


    query_order = """
        SELECT 
            o.id AS order_id,
            o.buyer_id,
            o.order_status,
            o.order_date,
            o.order_address,
            u.id AS user_id,
            u.first_name,
            u.last_name,
            u.email,
            u.phone,
            u.address AS user_address,
            u.user_name
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        WHERE o.buyer_id = :buyer_id AND LOWER(o.order_status) = :status
    """
    order_row = await database.fetch_one(query_order, values={"buyer_id": buyer_id, "status": "temp"})
    if not order_row:
        return None

    query_items = """
        SELECT 
            iio.id AS iio_id,
            iio.order_id,
            i.id AS item_id,
            i.item_name,
            i.price,
            i.amount_in_stock,
            i.image_url,
            iio.amount_in_order
        FROM item_in_order iio
        JOIN item i ON iio.item_id = i.id
        WHERE iio.order_id = :order_id
    """
    item_rows = await database.fetch_all(query_items, values={"order_id": order_row["order_id"]})

    order_items = []
    total_price = 0.0
    total_amount = 0

    for row in item_rows:
        item_instance = ItemResponse(
            id=int(row["item_id"]),
            item_name=row["item_name"],
            price=float(row["price"]),
            amount_in_stock=int(row["amount_in_stock"]),
            image_url=row["image_url"] or "https://katzr.net/a0cf43"
        )

        order_item_instance = ItemInOrderResponse(
            id=int(row["iio_id"]),
            order_id=int(row["order_id"]),
            item=item_instance,
            amount_in_order=int(row["amount_in_order"]),
            total_price=float(row["price"]) * int(row["amount_in_order"])
        )

        order_items.append(order_item_instance)
        total_price += order_item_instance.total_price
        total_amount += int(row["amount_in_order"])

    customer_instance = UserResponse(
        id=int(order_row["user_id"]),
        first_name=order_row["first_name"],
        last_name=order_row["last_name"],
        email=order_row["email"],
        phone=order_row["phone"],
        address=order_row["user_address"],
        user_name=order_row["user_name"]
    )

    order= OrderResponse(
        id=int(order_row["order_id"]),
        order_status=order_row["order_status"],
        customer=customer_instance,
        order_date=order_row["order_date"],
        order_address=order_row["order_address"],
        total_price=total_price,
        order_items=order_items,
        item_amount=total_amount
    )
    order_json = order.model_dump_json()
    cache_repository.create_cache_entity(temp_order_cache_key, order_json)

    return order


## close a temp order
async def close_order(order_id: int):
    query = f"""
        UPDATE {TABLE_NAME}
        SET order_status = :status,
            order_date = :order_date
        WHERE id = :order_id
    """
    values = {
        "status": "close",
        "order_date": datetime.now(),
        "order_id": order_id
    }

    await database.execute(query, values)

    buyer_id=await get_buyer_id_by_order_id(order_id)
    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(f"order_{order_id}")
    cache_repository.remove_cache_entity(f"user_order_{buyer_id}")
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")


async def get_closed_orders_summary_by_user(user_id: int) -> List[OrderSummary]:
    query = f"""
    SELECT 
        o.id AS order_id,
        o.order_date,
        o.order_address,
        SUM(iio.amount_in_order) AS total_items,
        SUM(iio.amount_in_order * i.price) AS total_price
    FROM {TABLE_NAME} o
    JOIN item_in_order iio ON iio.order_id = o.id
    JOIN item i ON i.id = iio.item_id
    WHERE o.buyer_id = :user_id AND o.order_status = 'close'
    GROUP BY o.id, o.order_date
    ORDER BY o.order_date DESC;
    """
    orders = await database.fetch_all(query, values={"user_id": user_id})

    return [OrderSummary(
        order_id=o["order_id"],
        order_date=o["order_date"],
        order_address=o["order_address"],
        total_items=int(o["total_items"]),
        total_price=float(o["total_price"])
    ) for o in orders]