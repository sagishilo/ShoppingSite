from typing import List, Optional

from model.item import Item
from model.item_in_order_response import ItemInOrderResponse
from model.item_response import ItemResponse
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_status import OrderStatus
from model.user_response import UserResponse
from repository.database import database

TABLE_NAME = "orders"


## Returns an order by id
async def get_by_id(order_id: int) -> Optional[OrderResponse]:
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
            item_in_order.amount_in_order
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
            item_name=row["item_name"],
            price=row["price"],
        )

        order_item_instance = ItemInOrderResponse(
            item=item_instance,
            amount_in_order=row["amount_in_order"],
            total_price=float(row["price"]) * row["amount_in_order"],
            order_id= order_id
        )
        order_items.append(order_item_instance)
        total_price += order_item_instance.total_price
        total_amount += row["amount_in_order"]

    customer_instance = UserResponse(
        user_id=order_row["buyer_id"],
        first_name=order_row["first_name"],
        last_name=order_row["last_name"],
        email=order_row["email"],
        phone=order_row["phone"],
        address=order_row["user_address"],
        user_name=order_row["user_name"]
    )

    return OrderResponse(
        id=order_row["order_id"],
        order_status=order_row["order_status"],
        customer=customer_instance,
        order_date=order_row["order_date"],
        order_address=order_row["order_address"],
        total_price=total_price,
        order_items=order_items,
        item_amount=total_amount
)



async def get_all() -> List[OrderResponse]:
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
                item.id,
                item.item_name,
                item.price,
                item.amount_in_stock,
                item_in_order.amount_in_order
            FROM item_in_order
            JOIN item ON item_in_order.item_id = item.id
            WHERE item_in_order.order_id = :order_id;
        """
        item_rows = await database.fetch_all(query_items, values={"order_id": order_row["order_id"]})

        order_items = []
        total_price = 0.0
        total_amount = 0

        for row in item_rows:
            item_instance = ItemResponse(
                item_name=row["item_name"],
                price=row["price"],
            )

            order_item_instance = ItemInOrderResponse(
                item=item_instance,
                amount_in_order=row["amount_in_order"],
                total_price=float(row["price"]) * row["amount_in_order"]
            )
            order_items.append(order_item_instance)
            total_price += order_item_instance.total_price
            total_amount += row["amount_in_order"]

        customer_instance = UserResponse(
            user_id=order_row["user_id"],
            first_name=order_row["first_name"],
            last_name=order_row["last_name"],
            email=order_row["email"],
            phone=order_row["phone"],
            address=order_row["user_address"],
            user_name=order_row["user_name"]
        )

        all_orders.append(
            OrderResponse(
                id=order_row["order_id"],
                order_status=order_row["order_status"],
                customer=customer_instance,
                order_date=order_row["order_date"],
                order_address=order_row["order_address"],
                total_price=total_price,
                order_items=order_items,
                item_amount=total_amount
            )
        )

    return all_orders


## Returns all orders by user id
async def get_all_by_user(buyer_id: int) -> List[OrderResponse]:
    query_orders = """
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
                WHERE buyer_id= :buyer_id
                """
    orders_rows = await database.fetch_all(query_orders,values={"buyer_id": buyer_id})
    all_orders = []

    for order_row in orders_rows:
        query_items = """
                SELECT 
                    item.id,
                    item.item_name,
                    item.price,
                    item.amount_in_stock,
                    item_in_order.amount_in_order
                FROM item_in_order
                JOIN item ON item_in_order.item_id = item.id
                WHERE item_in_order.order_id = :order_id;
            """
        item_rows = await database.fetch_all(query_items, values={"order_id": order_row["order_id"]})

        order_items = []
        total_price = 0.0
        total_amount = 0

        for row in item_rows:
            item_instance = ItemResponse(
                item_name=row["item_name"],
                price=row["price"],
            )

            order_item_instance = ItemInOrderResponse(
                item=item_instance,
                amount_in_order=row["amount_in_order"],
                total_price=float(row["price"]) * row["amount_in_order"]
            )
            order_items.append(order_item_instance)
            total_price += order_item_instance.total_price
            total_amount += row["amount_in_order"]

        customer_instance = UserResponse(
            user_id=order_row["user_id"],
            first_name=order_row["first_name"],
            last_name=order_row["last_name"],
            email=order_row["email"],
            phone=order_row["phone"],
            address=order_row["user_address"],
            user_name=order_row["user_name"]
        )

        all_orders.append(
            OrderResponse(
                id=order_row["order_id"],
                order_status=order_row["order_status"],
                customer=customer_instance,
                order_date=order_row["order_date"],
                order_address=order_row["order_address"],
                total_price=total_price,
                order_items=order_items,
                item_amount=total_amount
            )
        )

    return all_orders


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
    return result


## Deletes a specific order
async def delete_order(order_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id = :order_id"
    values = {"order_id": order_id}
    await database.execute(query, values)
    return order_id


async def get_temp_order_by_user(buyer_id: int) -> Optional[OrderResponse]:
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
        WHERE buyer_id = :buyer_id AND LOWER(order_status) = :status
    """

    order_row = await database.fetch_one(
        query_order,
        values={"buyer_id": buyer_id, "status": "temp"}
    )
    if not order_row:
        return None

    query_items = """
            SELECT 
                item.id,
                item.item_name,
                item.price,
                item.amount_in_stock,
                item_in_order.amount_in_order
            FROM item_in_order
            JOIN item ON item_in_order.item_id = item.id
            WHERE item_in_order.order_id = :order_id;
        """
    item_rows = await database.fetch_all(query_items, values={"order_id": order_row["order_id"]})

    order_items = []
    total_price = 0.0
    total_amount = 0

    for row in item_rows:
        item_instance = ItemResponse(
            item_name=row["item_name"],
            price=row["price"],
        )

        order_item_instance = ItemInOrderResponse(
            item=item_instance,
            amount_in_order=row["amount_in_order"],
            total_price=float(row["price"]) * row["amount_in_order"]
        )
        order_items.append(order_item_instance)
        total_price += order_item_instance.total_price
    customer_instance = UserResponse(
        user_id=order_row["buyer_id"],
        first_name=order_row["first_name"],
        last_name=order_row["last_name"],
        email=order_row["email"],
        phone=order_row["phone"],
        address=order_row["user_address"],
        user_name=order_row["user_name"]
    )

    return OrderResponse(
        id=order_row["order_id"],
        order_status=order_row["order_status"],
        customer=customer_instance,
        order_date=order_row["order_date"],
        order_address=order_row["order_address"],
        total_price=total_price,
        order_items=order_items,
        item_amount=total_amount
    )
