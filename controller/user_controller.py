from typing import List
from fastapi import HTTPException
from fastapi import APIRouter
from model.user import User
from repository import user_repository

router = APIRouter(prefix="/user", tags=["user"])



## Returns user
## gets-> int
## returns -> User
@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    try:
        return await user_repository.get_by_id(user_id)   ###################user_service
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


##Returns all users
## returns -> List of Users
@router.get("/", response_model=List[User])
async def get_users():
    try:
        return await user_repository.get_all()          ###################user_service
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



##Creates a new user
## gets-> JSON of User
## returns -> int (user id)
@router.post("/")
async def create_user(user: User):
    try:
        print("this is user " + str(dict(user)))
        return await user_repository.create_user(user)        ###################user_service
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



##Deletes a specific user and all votes they have made
## gets-> int (user id)
## returns -> str message
@router.delete("/{user_id}", response_model=int)
async def delete_user(user_id: int):
    try:
        return await user_repository.delete_user(user_id)         ###################user_service
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




## Updates an existing user
## gets -> JSON of User
## returns -> User
@router.put("/{user_id}", response_model=str)
async def update_user(user_id: int, updated_user: User):
    try:
        await user_repository.update_user(user_id, updated_user)  ###################user_service
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

