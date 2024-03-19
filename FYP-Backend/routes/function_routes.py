from fastapi import APIRouter
from models.function import Function
from config.database import functions_collection
from schemas.schemas import individual_serial, list_serial
from bson import ObjectId



function_router = APIRouter()

@function_router.post("/create_function")
def create_function(function: Function):
    existing_func = functions_collection.find_one({"function_name": function.function_name})

    if existing_func:
        return {
            "message":"A function with this name already exists!"
        }
    
    result = functions_collection.insert_one(dict(function))
    return {
        "message":"Function created successfully!"
    }


