import json
from typing import Optional
from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from model.item_response import ItemResponse
from repository import cache_repository, order_repository
from repository.database import database

TABLE_NAME = "item_in_order"

async def get_by_id(item_in_order_id: int):
    cache_key=f"iio_{item_in_order_id}"

    if cache_repository.is_key_exists(cache_key):
        iio_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return ItemInOrderResponse(**iio_dict)

    query = f"""
        SELECT 
            iio.id AS iio_id,
            iio.order_id,
            i.id AS item_id,
            i.item_name,
            i.price,
            i.image_url,
            i.amount_in_stock,
            iio.amount_in_order,
            (i.price * iio.amount_in_order) AS total_price
        FROM {TABLE_NAME} iio
        JOIN item i ON iio.item_id = i.id
        WHERE iio.id = :iio_id;
    """

    row = await database.fetch_one(query, {"iio_id": item_in_order_id})
    if not row:
        return None

    data = dict(row)

    item_data = ItemResponse(
        id=int(data["item_id"]),
        item_name=str(data["item_name"]),
        price=float(data["price"]),
        amount_in_stock=int(data["amount_in_stock"]),
        image_url=str(data.get("image_url") or "")
    )

    iio= ItemInOrderResponse(
        id=int(data["iio_id"]),
        order_id=int(data["order_id"]),
        item=item_data,
        amount_in_order=int(data["amount_in_order"]),
        total_price=float(data["total_price"])
    )
    iio_json = json.dumps(iio.model_dump())
    cache_repository.create_cache_entity(cache_key, iio_json)

    return iio


async def get_order_id_by_iio_id(iio_id: int):
    query = f"SELECT order_id FROM {TABLE_NAME} WHERE id=:iio_id"
    row = await database.fetch_one(query, {"iio_id": iio_id})
    if not row:
        return None
    return int(row["order_id"])



async def is_in_order(item_id: int, order_id: int):
    query = f"""
        SELECT  
            iio.*, 
            i.item_name, 
            i.price, 
            i.image_url,
            i.amount_in_stock
        FROM {TABLE_NAME} iio
        JOIN item i ON iio.item_id = i.id
        WHERE iio.order_id = :order_id AND iio.item_id = :item_id;
    """
    row = await database.fetch_one(query, {"item_id": item_id, "order_id": order_id})

    if row:
        data = dict(row)
        return ItemInOrderResponse(
            id=int(data["id"]),
            order_id=int(data["order_id"]),
            item=ItemResponse(
                id=int(data["item_id"]),
                item_name=data["item_name"],
                price=float(data["price"]),
                amount_in_stock=int(data["amount_in_stock"]),
                image_url=data.get("image_url", "")
            ),
            amount_in_order=int(data["amount_in_order"]),
            total_price=float(data["price"] * int(data["amount_in_order"]))
        )
    return None


async def get_id_by_item_and_order(item_id: int, order_id: int) -> Optional[int]:
    query = f"SELECT id FROM {TABLE_NAME} WHERE item_id = :item_id AND order_id = :order_id"
    row = await database.fetch_one(query, {"item_id": item_id, "order_id": order_id})
    return row["id"] if row else None


async def get_all_item_ids_by_order(order_id: int):
    query = f"SELECT item_id ,amount_in_order FROM {TABLE_NAME} WHERE order_id = :order_id"
    rows = await database.fetch_all(query, {"order_id": order_id})
    return rows


async def get_iio_ids_order_ids_buyer_ids_by_item_id(item_id: int):
    query = f"""
    SELECT 
        iio.id, 
        iio.order_id, 
        o.buyer_id 
    FROM {TABLE_NAME} iio
    JOIN `orders` o ON iio.order_id = o.id
    WHERE iio.item_id = :item_id
    """
    rows = await database.fetch_all(query, {"item_id": item_id})
    return rows




async def get_all_by_order_id(order_id: int):
    cache_key=f"iio_order_{order_id}"
    if cache_repository.is_key_exists(cache_key):
        iio_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return [ItemInOrderResponse(**item) for item in iio_dict]


    query = f"""
    SELECT  
        i.id AS item_id,
        i.item_name,
        i.price,
        i.image_url,
        i.amount_in_stock,
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
            amount_in_stock=int(data["amount_in_stock"]),
            image_url=data.get("image_url") or "https://katzr.net/a0cf43"
        )

        iio_obj = ItemInOrderResponse(
            id=int(data["iio_id"]),
            item=item_obj,
            amount_in_order=int(data["amount_in_order"]),
            total_price=float(data["price"]) * int(data["amount_in_order"]),
            order_id=int(data["order_id"])
        )
        formatted_results.append(iio_obj)

    items_json = json.dumps([iio.model_dump() for iio in formatted_results])
    cache_repository.create_cache_entity(cache_key, items_json)

    return formatted_results


async def add_item_to_order(item: ItemInOrder) -> Optional[int]:
    cache_key=f"iio_order_{item.order_id}"

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

    cache_repository.remove_cache_entity(cache_key)
    cache_repository.remove_cache_entity(f"order_{item.order_id}")
    buyer_id=await order_repository.get_buyer_id_by_order_id(item.order_id)
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")
    cache_repository.remove_cache_entity(f"orders_user_{buyer_id}")



    return new_iio_id



async def update_item_amount_in_order(item_in_order: ItemInOrderResponse, new_amount_in_order: int) -> Optional[int]:
    cache_key_iio=f"iio_{item_in_order.id}"
    cache_key_order=f"iio_order_{item_in_order.order_id}"


    query = f"""
    UPDATE {TABLE_NAME}
    SET amount_in_order = :new_amount_in_order
    WHERE id = :item_in_order_id;
    """
    values = {
        "new_amount_in_order": new_amount_in_order,
        "item_in_order_id": item_in_order.id
    }
    rows_updated = await database.execute(query=query, values=values)
    cache_repository.remove_cache_entity(cache_key_iio)
    cache_repository.remove_cache_entity(cache_key_order)
    cache_repository.remove_cache_entity(f"order_{item_in_order.order_id}")
    buyer_id = await order_repository.get_buyer_id_by_order_id(item_in_order.order_id)
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")
    cache_repository.remove_cache_entity(f"orders_user_{buyer_id}")


    return rows_updated



async def delete_item_in_order_by_id(item_in_order_id: int) -> Optional[int]:
    cache_key_iio=f"iio_{item_in_order_id}"
    order_id=await get_order_id_by_iio_id(item_in_order_id)
    cache_key_order=f"iio_order_{order_id}"

    query = f"""
    DELETE FROM {TABLE_NAME}
    WHERE id = :item_in_order_id;
    """
    values = {"item_in_order_id": item_in_order_id}

    await database.execute(query=query, values=values)

    cache_repository.remove_cache_entity(cache_key_iio)
    cache_repository.remove_cache_entity(cache_key_order)
    cache_repository.remove_cache_entity(f"order_{order_id}")
    buyer_id = await order_repository.get_buyer_id_by_order_id(order_id)
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")
    cache_repository.remove_cache_entity(f"orders_user_{buyer_id}")






async def order_deleted(order_id: int) -> Optional[int]:
    cache_key_order=f"iio_order_{order_id}"

    query = f"""
    DELETE FROM {TABLE_NAME}
    WHERE order_id = :order_id;
    """
    values = {"order_id": order_id}

    items = await get_all_by_order_id(order_id)
    for item in items:
        cache_repository.remove_cache_entity(f"iio_{item.id}")
    cache_repository.remove_cache_entity(cache_key_order)
    cache_repository.remove_cache_entity(f"order_{order_id}")
    buyer_id = await order_repository.get_buyer_id_by_order_id(order_id)
    cache_repository.remove_cache_entity(f"temp_{buyer_id}")
    cache_repository.remove_cache_entity(f"orders_user_{buyer_id}")


    await database.execute(query=query, values=values)



async def item_deleted(item_id: int) -> int:

    query = f"""
    DELETE FROM {TABLE_NAME}
    WHERE item_id = :item_id;
    """

    rows=await get_iio_ids_order_ids_buyer_ids_by_item_id(item_id)
    for row in rows:
        iio_id=row["id"]
        order_id = row["order_id"]
        buyer_id = row["buyer_id"]
        cache_repository.remove_cache_entity(f"iio_{iio_id}")
        cache_repository.remove_cache_entity(f"iio_order_{order_id}")
        cache_repository.remove_cache_entity(f"order_{order_id}")
        cache_repository.remove_cache_entity(f"temp_{buyer_id}")
        cache_repository.remove_cache_entity(f"orders_user_{buyer_id}")

    return await database.execute(query, {"item_id": item_id})

