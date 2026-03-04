from typing import List, Optional

from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from repository import item_in_order_repository
from model.exceptions import CustomExceptions
from repository.item_in_order_repository import is_in_order
from service import order_service, item_service

ex = CustomExceptions()

## Checks if an item in order exists by its id
## Returns True if exists, False otherwise
async def validate_item_in_order_exists(item_in_order_id: int) -> bool:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    return item_in_order is not None


## Returns an item in order by its id
## Raises exception if not found
async def get_item_in_order_by_id(item_in_order_id: int) -> ItemInOrderResponse:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    if not item_in_order:
        raise ex.item_in_order_not_found_exception()
    return item_in_order


## Returns all items in a specific order
async def get_all_items_by_order_id(order_id: int) -> List[ItemInOrderResponse]:
    return await item_in_order_repository.get_all_by_order_id(order_id)


## Adds a new item to an order
## Returns the id of the newly created item_in_order record
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
        await item_in_order_repository.update_item_amount_in_order(iio_id, new_amount)
        return iio_id

    await item_service.update_amount(item.item_id, item.amount_in_order)
    return await item_in_order_repository.add_item_to_order(item)


## Updates the amount of an item in order
## Returns the number of rows updated
async def update_item_amount_in_order(item_in_order: ItemInOrder, new_amount_in_order: int):
    if not await is_in_order(item_in_order.item_id, item_in_order.order_id):
        raise ex.item_in_order_not_found_exception()
    await item_in_order_repository.update_item_amount_in_order(item_in_order.id, new_amount_in_order)


## Deletes an item from an order by its id
## Returns the number of rows deleted
async def delete_item_in_order_by_id(item_in_order_id: int) -> int:
    if not await validate_item_in_order_exists(item_in_order_id):
        raise ex.item_in_order_not_found_exception()
    return await item_in_order_repository.delete_item_in_order_by_id(item_in_order_id)
