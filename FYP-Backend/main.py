from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from routes.user_routes import user_router
from routes.function_routes import function_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(function_router)



   