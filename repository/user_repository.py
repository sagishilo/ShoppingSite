from typing import Optional, List
import json
from model.login_request import LoginRequest
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import cache_repository
from repository.database import database
from passlib.hash import bcrypt
all_cache_key = "all_users"
TABLE_NAME = "users"




##Returns a specific user by its id
async def get_by_id(user_id: int) -> Optional[UserResponse]:
    cache_key=f"user_{user_id}"
    if cache_repository.is_key_exists(cache_key):
        user_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return UserResponse(**user_dict)

    query = f"""
        SELECT 
            id,
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name
        FROM {TABLE_NAME}
        WHERE id = :user_id;
    """
    row = await database.fetch_one(query, values={"user_id": user_id})
    if row is None:
        return None
    user= UserResponse(**dict(row))
    user_json = json.dumps(user.model_dump())
    cache_repository.create_cache_entity(cache_key, user_json)
    return user




##Returns all users
async def get_all() -> List[UserResponse]:
    if cache_repository.is_key_exists(all_cache_key):
        users_dict = json.loads(cache_repository.get_cache_entity(all_cache_key))
        return [UserResponse(**user) for user in users_dict]

    query = f"""
        SELECT 
            id AS user_id,
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name,
        FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    users= [UserResponse(**dict(row)) for row in result]
    users_json = json.dumps([user.model_dump() for user in users])
    cache_repository.create_cache_entity(all_cache_key, users_json)
    return users




##Creates a new user
async def create_user(new_user: UserRequest, hashed_password: str) -> int:
    query = f"""
        INSERT INTO {TABLE_NAME} 
        (first_name, last_name, email, phone, address, user_name, hashed_password)
        VALUES (:first_name, :last_name, :email, :phone, :address, :user_name, :hashed_password)
    """
    user_dict = new_user.model_dump()
    user_dict.pop("password", None)
    user_dict.pop("id", None)
    values = {**user_dict, "hashed_password": hashed_password}

    await database.execute(query, values)
    row = await database.fetch_one("SELECT LAST_INSERT_ID() AS id")
    cache_repository.remove_cache_entity(all_cache_key)
    return row["id"]





##Updates a specific user
async def update_user(user_id: int, updated_user: UserRequest, hashed_password: str) -> int:
    cache_key=f"user_{user_id}"

    query = f"""
        UPDATE {TABLE_NAME}
        SET first_name = :first_name,
            last_name = :last_name,
            email = :email,
            phone = :phone,
            address = :address,
            user_name = :user_name,
            hashed_password = :hashed_password
        WHERE id = :user_id
    """
    user_dict = updated_user.model_dump()
    user_dict.pop("password", None)
    user_dict.pop("id", None)
    values = {**user_dict, "hashed_password": hashed_password, "user_id": user_id}

    async with database.transaction():
        cache_repository.remove_cache_entity(all_cache_key)
        cache_repository.remove_cache_entity(cache_key)

        return await database.execute(query, values)




##Deletes a specific user by its id
async def delete_user(user_id: int):
    cache_key=f"user_{user_id}"

    query = f"DELETE FROM {TABLE_NAME} WHERE id = :user_id"
    await database.execute(query, {"user_id": user_id})

    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(cache_key)
    return user_id





##Returns a user by its username
async def get_by_user_name(user_name: str) -> Optional[UserResponse]:
    query = f"""
        SELECT 
            id,
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name
        FROM {TABLE_NAME}
        WHERE user_name = :user_name;
    """
    row = await database.fetch_one(query, values={"user_name": user_name})
    if row is None:
        return None
    return UserResponse(**dict(row))



##Authenticates a user and returns the user id if valid
async def user_login(login_request: LoginRequest) -> Optional[int]:
    query = f"""
        SELECT id, hashed_password
        FROM {TABLE_NAME}
        WHERE user_name = :user_name
    """
    row = await database.fetch_one(query, values={"user_name": login_request.user_name})

    if row is None:
        return None
    row_dict = dict(row._mapping)
    hashed = row_dict.get("hashed_password")
    user_id = row_dict.get("id")

    if hashed and bcrypt.verify(login_request.password, hashed):
        return user_id

    return None