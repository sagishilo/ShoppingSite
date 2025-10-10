from typing import Optional

from repository.database import database

TABLE_NAME = "item_in_order"

async def get_by_id(item_in_order_id: int):
    query = f"""
    SELECT 
    item_in_order.id AS item_in_order_id,
    item.item_name,
    item.price,
    item.amount_in_stock,
    item.id AS item_id,
    item_in_order.amount_in_order,
    (item.price * item_in_order.amount_in_order) AS total_price_in_order
    FROM {TABLE_NAME}
    JOIN item ON item_in_order.item_id = item.id
    JOIN orders ON item_in_order.order_id = orders.id
    WHERE item_in_order.id = :item_in_order_id;
    """
    result = await database.fetch_one(query, values={"item_in_order_id": item_in_order_id})
    if result:
        return result
    else:
        return None



async def get_all_by_order_id(order_id: int):
    query = f"""
    SELECT 
        item_in_order.id AS item_in_order_id,
        item.item_name AS item_name,
        item.price AS item_price,
        item.amount_in_stock AS item_amount_in_stock,
        item.id AS item_id,
        item_in_order.amount_in_order AS amount_in_order,
        (item.price * item_in_order.amount_in_order) AS total_price_in_order
    FROM {TABLE_NAME}
    JOIN item ON item_in_order.item_id = item.id
    WHERE item_in_order.order_id = :order_id;
    """

    results = await database.fetch_all(query, {"order_id": order_id})
    return results



async def add_item_to_order(order_id: int, item_id: int, amount_in_order: int) -> Optional[int]:
    query = f"""
    INSERT INTO {TABLE_NAME} (order_id, item_id, amount_in_order)
    VALUES (:order_id, :item_id, :amount_in_order);
    """
    values = {
        "order_id": order_id,
        "item_id": item_id,
        "amount_in_order": amount_in_order
    }
    new_iio_id = await database.execute(query=query, values=values)
    return new_iio_id



async def update_item_amount_in_order(item_in_order_id: int, new_amount_in_order: int) -> Optional[int]:

    query = f"""
    UPDATE {TABLE_NAME}
    SET amount_in_order = :new_amount_in_order
    WHERE id = :item_in_order_id;
    """
    values = {
        "new_amount_in_order": new_amount_in_order,
        "item_in_order_id": item_in_order_id
    }
    rows_updated = await database.execute(query=query, values=values)
    return rows_updated



async def delete_item_in_order_by_id(item_in_order_id: int) -> Optional[int]:
    query = """
    DELETE FROM item_in_order
    WHERE id = :item_in_order_id;
    """
    values = {"item_in_order_id": item_in_order_id}
    rows_deleted = await database.execute(query=query, values=values)
    return rows_deleted
