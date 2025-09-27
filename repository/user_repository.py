from typing import Optional, List
from model.user import User
from repository.database import database

TABLE_NAME = "users"

## Returns a user by id
async def get_by_id(user_id: int) ->Optional[User]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :user_id;
    """
    result = await database.fetch_one(query, values={"user_id": user_id})
    if result:
        return User(**result)
    else:
        return None


## Returns all users
async def get_all() ->List[User]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    return result


## Creates a new user
async def create_user(new_user: User)-> int:
    query= f"""
    INSERT INTO {TABLE_NAME} (first_name,last_name, email, phone, address, user_name, password )
    VALUES(:first_name, :last_name, :email, :phone, :address, :user_name, :password)
    """
    values={"first_name": new_user.first_name,
            "last_name":new_user.last_name,
            "email":new_user.email,
            "phone":new_user.phone,
            "address":new_user.address,
            "user_name":new_user.user_name,
            "password":new_user.password}

    last_record_id = await database.execute(query, values)
    return last_record_id


## Updates an existing user
async def update_user(user_id: int, updated_user: User) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET first_name = :first_name,
        last_name = :last_name,
        email = :email,
        phone = :phone,
        address = :address,
        user_name = :user_name,
        password = :password
    WHERE id = :user_id
    """
    values = {
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "email": updated_user.email,
        "phone": updated_user.phone,
        "address": updated_user.address,
        "user_name": updated_user.user_name,
        "password": updated_user.password,
        "user_id": user_id,
    }

    async with database.transaction():
        result = await database.execute(query, values)
    return result


##Deletes a specific user
async def delete_user(user_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id= :user_id"
    values ={"user_id":user_id }
    await database.execute(query, values)

