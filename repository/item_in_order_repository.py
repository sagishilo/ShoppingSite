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
    
