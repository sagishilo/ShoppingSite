
from typing import List, Optional
from model.exceptions import CustomExceptions
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_status import OrderStatus
from model.order_summary import OrderSummary
from repository import order_repository, user_repository
from service import item_in_order_service

ex = CustomExceptions()


## Checks if an order exists by id
## Returns True if exists, False otherwise
async def validate_order_exists(order_id: int) -> bool:
    existing_order = await order_repository.get_by_id(order_id)
    return existing_order is not None

## Checks if a user exists by id
## Returns True if exists, False otherwise
async def validate_user_exists(user_id: int) -> bool:
    user = await user_repository.get_by_id(user_id)
    return user is not None

## Checks if the order status is valid
## Returns True if valid, False otherwise
async def validate_order_status(status: str) -> bool:
    try:
        OrderStatus(status)
        return True
    except ValueError:
        return False

## Returns all orders
async def get_all() -> List[OrderResponse]:
    orders_list= await order_repository.get_all()
    return orders_list

## Returns all closed orders for user
async def get_closed_orders_summary_by_user(user_id: int) -> List[OrderSummary]:
    if not await validate_user_exists(user_id):
        raise ex.user_not_found_exception()
    orders_list= await order_repository.get_closed_orders_summary_by_user(user_id)
    return orders_list

## Returns an order by id
## Raises an exception if order is not found
async def get_order_by_id(order_id: int) -> OrderResponse:
    order = await order_repository.get_by_id(order_id)
    if not order:
        raise ex.order_not_found_exception()
    return order


## Returns all orders
## Returns all orders for a specific user
## Raises an exception if user not found
async def get_all_orders_by_user(buyer_id: int) -> List[OrderResponse]:
    if not await validate_user_exists(buyer_id):
        raise ex.user_not_found_exception()
    return await order_repository.get_all_by_user(buyer_id)


## Creates a new order
## Checks if user exists and order status is valid
async def create_order(new_order: OrderRequest) -> int:
    if not await validate_user_exists(new_order.buyer_id):
        raise ex.user_not_found_exception()
    if not await validate_order_status(new_order.order_status.value):
        raise ex.invalid_order_status_exception()
    if new_order.order_status.value == "temp":
        if await order_repository.get_temp_order_by_user(new_order.buyer_id) is not None:
            raise ex.temp_order_exist()
    return await order_repository.create_order(new_order)



## Updates an existing order
## Checks if order exists, user exists, and order status is valid
async def update_order(order_id: int, updated_order: OrderRequest) -> int:
    if not await validate_order_exists(order_id):
        raise ex.order_not_found_exception()
    if not await validate_user_exists(updated_order.buyer_id):
        raise ex.user_not_found_exception()
    if not await validate_order_status(updated_order.order_status.value):
        raise ex.invalid_order_status_exception()
    return await order_repository.update_order(order_id, updated_order)



## Deletes an order and all it's items
## Raises an exception if order does not exist
async def delete_order(order_id: int) -> Optional[str]:
    if not await validate_order_exists(order_id):
        raise ex.order_not_found_exception()
    iio=await item_in_order_service.get_all_items_by_order_id(order_id)
    for item in iio:
        await item_in_order_service.delete_item_in_order_by_id(item.item.id)
    await order_repository.delete_order(order_id)
    return f"The order with id {order_id} was deleted"



##gets the open order by user id
async def get_temp_order_by_user(buyer_id: int) -> Optional[OrderResponse]:
    temp_order=await order_repository.get_temp_order_by_user(buyer_id)
    if temp_order is not None:
        return temp_order
    else:
        return None

## Updates an existing temp order as close
## Checks if order exists
async def close_order(order_id: int):
    if await validate_order_exists(order_id):
        await order_repository.close_order(order_id)
    else:
        raise ex.order_not_found_exception()