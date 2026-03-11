from fastapi import FastAPI
from controller.user_controller import router as user_router
from controller.item_controller import router as item_router
from controller.order_controller import router as order_router
from controller.item_in_order_controller import router as iio_router
from controller.favorite_item_controller import router as fav_router
from controller.gpt_controller import router as gpt_router

from repository.database import database

app=FastAPI()

@app.on_event("startup")
async def startup(): ##async - every line happens without waiting the lone before to finish
    await database.connect() ##await - forces the def to wait until the line finished

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/ping")
def ping():
    return {"message": "pong"}

app.include_router(user_router)
app.include_router(item_router)
app.include_router(order_router)
app.include_router(iio_router)
app.include_router(fav_router)
app.include_router(gpt_router)

