from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from routes.user_routes import user_router
from routes.function_routes import function_router




app = FastAPI()


app.include_router(user_router)
app.include_router(function_router)



