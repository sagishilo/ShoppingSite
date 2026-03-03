from typing import Optional
from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from model.item_response import ItemResponse
from repository.database import database

TABLE_NAME = "item_in_order"

async def get_by_id(item_in_order_id: int):
    query = """
    SELECT 
        item_in_order.order_id,
        item.id AS item_id,
        item.item_name,
        item.price,
        item.amount_in_stock,
        item_in_order.amount_in_order,
        (item.price * item_in_order.amount_in_order) AS total_price
    FROM item_in_order
    JOIN item ON item_in_order.item_id = item.id
    WHERE item_in_order.id = :item_in_order_id;
    """

    row = await database.fetch_one(query, {"item_in_order_id": item_in_order_id})
    if not row:
        return None

    row = dict(row)

    item = ItemResponse(
        item_name=row["item_name"],
        price=float(row["price"])
    )

    return ItemInOrderResponse(
        order_id=int(row["order_id"]),
        item=item,
        amount_in_order=int(row["amount_in_order"]),
        total_price=float(row["total_price"]),
    )



async def is_in_order(item_id: int, order_id: int):
    query = f"""
        SELECT * FROM {TABLE_NAME} 
        WHERE order_id = :order_id AND item_id = :item_id;
    """
    results = await database.fetch_one(query, {"item_id": item_id, "order_id": order_id})
    if results:
        return ItemInOrder(**dict(results))
    else:
        return None


async def get_all_by_order_id(order_id: int):
    query = f"""
    SELECT 
        item.id AS id,
        item.item_name AS item_name,
        item.price AS price,
        item.image_url AS image_url,
        item_in_order.amount_in_order AS amount_in_order,
        item_in_order.order_id AS order_id,
        (item.price * item_in_order.amount_in_order) AS total_price
    FROM {TABLE_NAME}
    JOIN item ON item_in_order.item_id = item.id
    WHERE item_in_order.order_id = :order_id;
    """

    results = await database.fetch_all(query, {"order_id": order_id})

    formatted_results = []
    for row in results:
        data = dict(row._mapping)

        item_obj = ItemResponse(
            id=int(data["id"]),
            item_name=data["item_name"],
            price=float(data["price"]),
            image_url=data.get("image_url", "")
        )

        iio_obj = ItemInOrderResponse(
            item=item_obj,
            amount_in_order=int(data["amount_in_order"]),
            total_price=float(data["total_price"]),
            order_id=int(data["order_id"])
        )
        formatted_results.append(iio_obj)

    return formatted_results


async def add_item_to_order(item: ItemInOrder) -> Optional[int]:
    query = f"""
    INSERT INTO {TABLE_NAME} (order_id, item_id, amount_in_order)
    VALUES (:order_id, :item_id, :amount_in_order);
    """
    values = {
        "order_id": item.order_id,
        "item_id": item.item_id,
        "amount_in_order": item.amount_in_order
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


async def item_deleted(item_id: int) -> int:
    query = """
    DELETE FROM item_in_order
    WHERE item_id = :item_id;
    """
    return await database.execute(query, {"item_id": item_id})

