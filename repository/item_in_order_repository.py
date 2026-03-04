from typing import Optional
from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from model.item_response import ItemResponse
from repository.database import database

TABLE_NAME = "item_in_order"

async def get_by_id(item_in_order_id: int):
    query = f"""
        SELECT 
            iio.id AS item_in_order_id,
            iio.order_id,
            i.id AS item_id,
            i.item_name,
            i.price,
            i.image_url,
            iio.amount_in_order,
            (i.price * iio.amount_in_order) AS total_price
        FROM {TABLE_NAME} iio
        JOIN item i ON iio.item_id = i.id
        WHERE iio.id = :item_in_order_id;
    """

    row = await database.fetch_one(query, {"item_in_order_id": item_in_order_id})
    if not row:
        return None

    data = dict(row)

    item_data = ItemResponse(
        id=int(data["item_id"]),
        item_name=str(data["item_name"]),
        price=float(data["price"]),
        image_url=str(data.get("image_url") or "")
    )

    return ItemInOrderResponse(
        order_id=int(data["order_id"]),
        item=item_data,
        amount_in_order=int(data["amount_in_order"]),
        total_price=float(data["total_price"])
    )


async def is_in_order(item_id: int, order_id: int):
    query = f"""
        SELECT 
            iio.*, 
            i.item_name, 
            i.price, 
            i.image_url
        FROM {TABLE_NAME} iio
        JOIN item i ON iio.item_id = i.id
        WHERE iio.order_id = :order_id AND iio.item_id = :item_id;
    """
    row = await database.fetch_one(query, {"item_id": item_id, "order_id": order_id})

    if row:
        data = dict(row)
        return ItemInOrderResponse(
            order_id=data["order_id"],
            item=ItemResponse(
                id=data["item_id"],
                item_name=data["item_name"],
                price=float(data["price"]),
                image_url=data.get("image_url", "")
            ),
            amount_in_order=data["amount_in_order"],
            total_price=float(data["price"] * data["amount_in_order"])
        )
    return None


async def get_id_by_item_and_order(item_id: int, order_id: int) -> Optional[int]:
    query = f"SELECT id FROM {TABLE_NAME} WHERE item_id = :item_id AND order_id = :order_id"
    row = await database.fetch_one(query, {"item_id": item_id, "order_id": order_id})
    return row["id"] if row else None



async def get_all_by_order_id(order_id: int):
    query = f"""
    SELECT 
        i.id AS item_id,
        i.item_name,
        i.price,
        i.image_url,
        iio.id AS iio_id,
        iio.amount_in_order,
        iio.order_id
    FROM {TABLE_NAME} iio
    JOIN item i ON iio.item_id = i.id
    WHERE iio.order_id = :order_id;
    """

    rows = await database.fetch_all(query, {"order_id": order_id})

    formatted_results = []
    for row in rows:
        data = dict(row)

        item_obj = ItemResponse(
            id=int(data["item_id"]),
            item_name=data["item_name"],
            price=float(data["price"]),
            image_url=data.get("image_url") or "https://katzr.net/a0cf43"
        )

        iio_obj = ItemInOrderResponse(
            item=item_obj,
            amount_in_order=int(data["amount_in_order"]),
            total_price=float(data["price"]) * int(data["amount_in_order"]),
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

