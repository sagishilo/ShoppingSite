from typing import Optional, List
from model.exceptions import CustomExceptions
from model.login_request import LoginRequest
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import user_repository
from passlib.context import CryptContext
from repository.database import database
from service import order_service, favorite_item_service, item_in_order_service
ex=CustomExceptions()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




## Hashes a plain password
## Returns hashed password

def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)



## Verifies a plain password against a hash
## Returns True if matched, False otherwise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)




## Checks if username exists
## Raises exception if not found

async def get_user_by_user_name(user_name: str) -> UserResponse:
    user= await user_repository.get_by_user_name(user_name)
    if not user:
        raise ex.user_not_found_exception()
    return user



## Checks if username is unique
## Returns True if unique, False otherwise

async def validate_unique_user_name(user_name: str) -> bool:
    existing_user = await user_repository.get_by_user_name(user_name)
    return existing_user is None



## Checks if user exists by id
## Raises exception if not found

async def get_by_id(user_id: int) -> Optional[UserResponse]:
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise ex.user_not_found_exception()
    return user




## Returns all users
async def get_all() -> List[UserResponse]:
    users_list= await user_repository.get_all()
    return users_list



## Creates a new user
## Checks username uniqueness, hashes password, saves user

async def create_user(new_user: UserRequest) -> UserResponse:
    if await validate_unique_user_name(new_user.user_name):
        hashed_password = get_password_hash(new_user.password)
        user_id = await user_repository.create_user(new_user, hashed_password)
        return await user_repository.get_by_id(user_id)
    else:
        print("username is already existing")
        raise ex.username_taken_exception()





## Updates an existing user
## Checks user existence, username uniqueness, hashes new password

async def update_user(user_id: int, updated_user: UserRequest):
    existing_user = await user_repository.get_by_id(user_id)
    if not existing_user:
        raise ex.user_not_found_exception()
    if updated_user.user_name != existing_user.user_name:
        is_unique = await validate_unique_user_name(updated_user.user_name)
        if not is_unique:
            raise ex.username_taken_exception()
    hashed_password = get_password_hash(updated_user.password)
    return await user_repository.update_user(user_id, updated_user, hashed_password)



## Deletes a user and all related data
## Checks user existence, deletes favorites, orders, items, user

async def delete_user(user_id: int) -> Optional[str]:
    existing_user = await user_repository.get_by_id(user_id)
    if not existing_user:
        raise ex.user_not_found_exception()
    async with database.transaction():
        await favorite_item_service.unfav_items_for_user(user_id)
        order_ids = await order_service.get_all_id_by_user(user_id)
        for o in order_ids:
            await item_in_order_service.delete_item_in_order_by_order_id(o)

        await order_service.delete_orders_for_user(user_id)
        await user_repository.delete_user(user_id)

    return f"The user with id {user_id} and all associated data were deleted"




## Logs in a user
## Verifies credentials, returns user if valid, raises exception if not found

async def user_login(login_request: LoginRequest) -> Optional[UserResponse]:
    user_id = await user_repository.user_login(login_request)
    if user_id:
        return await user_repository.get_by_id(user_id)
    raise ex.user_not_found_exception()
