from typing import List, Optional

from model.order import Order
from repository.database import database

TABLE_NAME = "orders"


## Returns an order by id
async def get_by_id(order_id: int) -> Optional[Order]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :order_id;
    """
    result = await database.fetch_one(query, values={"order_id": order_id})
    if result:
        return Order(**result)
    else:
        return None


## Returns all orders
async def get_all() -> List[Order]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    return [Order(**row) for row in result]


## Creates a new order
async def create_order(new_order: Order) -> int:
    query = f"""
    INSERT INTO {TABLE_NAME} (buyer_id, order_address, order_status)
    VALUES (:buyer_id, :order_address, :order_status)
    """
    values = {
        "buyer_id": new_order.buyer_id,
        "order_address": new_order.order_address,
        "order_status": new_order.order_status
    }

    last_record_id = await database.execute(query, values)
    return last_record_id


## Updates an existing order
async def update_order(order_id: int, updated_order: Order) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET buyer_id = :buyer_id,
        order_address = :order_address,
        order_status = :order_status
    WHERE id = :order_id
    """
    values = {
        "buyer_id": updated_order.buyer_id,
        "order_address": updated_order.order_address,
        "order_status": updated_order.order_status,
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
