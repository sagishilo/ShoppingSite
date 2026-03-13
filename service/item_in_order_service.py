from typing import List, Optional

from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from repository import item_in_order_repository
from model.exceptions import CustomExceptions
from repository.item_in_order_repository import is_in_order
from service import order_service, item_service

ex = CustomExceptions()

## Receives an item_in_order id
## Checks if the item exists in the order
## Returns True if it exists, False otherwise

async def validate_item_in_order_exists(item_in_order_id: int) -> bool:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    return item_in_order is not None



## Receives an item_in_order id
## Fetches the item in order from the repository
## Raises exception if not found, otherwise returns the item

async def get_item_in_order_by_id(item_in_order_id: int) -> ItemInOrderResponse:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    if not item_in_order:
        raise ex.item_in_order_not_found_exception()
    return item_in_order


## Receives an order id
## Fetches all items associated with that order
## Returns a list of ItemInOrderResponse objects

async def get_all_items_by_order_id(order_id: int) -> List[ItemInOrderResponse]:
    return await item_in_order_repository.get_all_by_order_id(order_id)




## Adds a new item to an order
## Checks if the order is closed and raises exception if it is
## Checks if the requested amount exceeds stock and raises exception if not enough
## Checks if the item is already in the order
## If yes, updates the amount in order and stock
## If the item is not in the order:
## Adds the item to the order
## Returns the item_in_order id

async def add_item_to_order(item: ItemInOrder) -> Optional[int]:
    order = await order_service.get_order_by_id(item.order_id)
    if order.order_status == "close":
        raise ex.closed_order()

    item_info = await item_service.get_full_item(item.item_id)
    if item.amount_in_order > item_info.amount_in_stock:
        raise ex.not_in_stock(item_info.amount_in_stock)

    existing_item = await item_in_order_repository.is_in_order(item.item_id, item.order_id)
    if existing_item:
        new_amount = existing_item.amount_in_order + item.amount_in_order
        await item_service.update_amount(item.item_id, item.amount_in_order)

        iio_id = await item_in_order_repository.get_id_by_item_and_order(item.item_id, item.order_id)
        iio=await item_in_order_repository.get_by_id(iio_id)
        await item_in_order_repository.update_item_amount_in_order(iio, new_amount)
        return iio_id

    return await item_in_order_repository.add_item_to_order(item)



## Receives an order id
## Updates the stock amounts of all items in that order
## Returns Nothing
async def stock_update(order_id: int):
    items= await item_in_order_repository.get_all_item_ids_by_order(order_id)
    for i in items:
        await item_service.update_amount(int(i["item_id"]), int(i["amount_in_order"]))



## Receives an ItemInOrderResponse object and a new amount
## Updates the amount of that item in the order
## Returns the number of rows updated, raises exception if item not found

async def update_item_amount_in_order(item_in_order: ItemInOrderResponse, new_amount_in_order: int):
    item_id = item_in_order.item.id
    order_id = item_in_order.order_id
    if not await is_in_order(item_id, order_id):
        raise ex.item_in_order_not_found_exception()
    rows_updated = await (item_in_order_repository.update_item_amount_in_order
                          (item_in_order, new_amount_in_order))
    if rows_updated == 0:
        raise ex.item_in_order_not_found_exception()
    return rows_updated


## Receives an item_in_order id
## Deletes that specific item from the order
## Returns the number of rows deleted, raises exception if item not found

async def delete_item_in_order_by_id(item_in_order_id: int) -> int:
    if not await validate_item_in_order_exists(item_in_order_id):
        raise ex.item_in_order_not_found_exception()
    return await item_in_order_repository.delete_item_in_order_by_id(item_in_order_id)


## Receives an order id
## Deletes all items associated with that order
## Returns Nothing

async def delete_item_in_order_by_order_id(order_id: int):
    await item_in_order_repository.order_deleted(order_id)


## Receives an item id
## Deletes all instances of that item from orders
## Returns the number of rows deleted, raises exception if item not found

async def delete_item_in_order_by_item_id(item_id: int) -> int:
    if not await item_service.get_item_by_id(item_id):
        raise ex.item_not_found_exception()
    return await item_in_order_repository.item_deleted(item_id)
