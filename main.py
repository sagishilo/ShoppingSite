from fastapi import FastAPI
from controller.user_controller import router as user_router
from controller.customer_controller import router as customer_router
from controller.customer_order_controller import router as customer_order_router
from controller.tv_maze_controller import router as tv_maze_router
from repository.database import databases

app=FastAPI()

@app.on_event("startup")
async def startup(): ##async - every line happens without waiting the lone before to finish
    await databases.connect() ##await - forces the def to wait until the line finished

@app.on_event("shutdown")
async def shutdown():
    await databases.disconnect()


app.include_router(user_router)
app.include_router(customer_router)
app.include_router(customer_order_router)
app.include_router(tv_maze_router)