from fastapi import FastAPI, APIRouter, Header, Response
from models.user import User
from config.database import users_collection
from bson import ObjectId
import os
import replicate
from config.database import functions_collection
import subprocess
from passlib.hash import bcrypt
from starlette.responses import FileResponse
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode as jwt_encode, decode as jwt_decode
from datetime import datetime, timedelta
from utils.access_token import create_access_token, decode_access_token
from models.user_login import UserLogin


os.environ["REPLICATE_API_TOKEN"] = "r8_GiOYTpAJsjXCRs8IxwO7fhBoYNqIBFi1KecAA"

user_router = APIRouter()

@user_router.get("/")
def get_user():
    return {"message": "hello"}

@user_router.post("/signup")
async def signup(user: User):
    # Check if user already exists

    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        return {
            "error" : "Can not create user!"
        }

    # Hash the password
    hashed_password = bcrypt.hash(user.password)
    user_dict = dict(user)
    user_dict["password"] = hashed_password
    
    # Create user in the database
    result = users_collection.insert_one(user_dict)

    if result:
        return {
            "message": "User created successfully",
        }
    





@user_router.post("/login")
async def login(user_login: UserLogin):
    user = users_collection.find_one({"email": user_login.email})
    if not user or not bcrypt.verify(user_login.password, user["password"]):
        return {
            "message" : "Uaser can not be logged in!"
        }

    # Generate JWT token with expiry time
    access_token_expires = timedelta(hours=48)
    access_token = create_access_token(data={"sub": str(user["_id"])}, expires_delta=access_token_expires)
    
    # Include access token in response headers
    response = Response()
    response.headers["Authorization"] = f"Bearer {access_token}"
    response.headers["token_type"] = "bearer"
    return {"message": "Login successful"}, response







# @user_router.get("/users/me")
# async def read_users_me(authorization: str = Header(...)):
#     token = authorization.split()[1]
#     payload = decode_access_token(token)
#     user_id = payload.get("sub")
#     # Now you have user_id, you can fetch the user details from the database
#     user = users_collection.find_one({"_id": ObjectId(user_id)})
#     if user:
#         return user
#     else:
#         raise HTTPException(status_code=404, detail="User not found")





@user_router.post("/prompt")
async def handlePrompt(prompt: str):

    # Update user prompts and generation count
    user_email = "abdullah@gmail.com"  # Assuming you have the user's email
    user = users_collection.find_one({"email": user_email})

    if user:
        # Update prompts array and increment generation_count
        users_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {
                "$push": {"prompts": prompt},
                "$inc": {"generation_count": 1}
            }
        )


    all_functions = functions_collection.find({})
    import_statements = [
        "import bpy\n",
        "import random\n",
        "import numpy as np\n",
        "import random\n"
    ]
    default_functions = [
        "\ndef delete_all_objects():\n\tfor object in bpy.data.objects:\n\t\tbpy.data.objects.remove(object)\n",
        "\ndef decrease_size(obj):\n\tobj.delta_scale = [ obj.delta_scale[0] - 1.4 / 1.5, obj.delta_scale[1] - 1.4 / 1.5, obj.delta_scale[2] - 1.4 / 1.5 ]\n",
        "\ndef add_shrinkwrap(data, target):\n\tcon = data.constraints.new('SHRINKWRAP')\n\tcon.target = target\n\tcon.shrinkwrap_type = 'PROJECT'\n\tcon.project_axis = 'NEG_Z'\n"
    ]

    function_docs = []
    func_name_and_code = []

    for function in all_functions:
        function_docs.append({
            "function_name" : function["function_name"],
            "function_docs": function["function_docs"],
            "function_params": function["function_params"]
        })

        func_name_and_code.append({
            "function_name" : function["function_name"],
            "function_code" : function["function_code"]
        })


    response_1 = replicate.run(
    "meta/llama-2-70b-chat:2d19859030ff705a87c746f7e96eea03aefb71f166725aee39692f1476566d48",
    input={
        "debug": True,
        "top_p": 1,
        "prompt": prompt,
        "temperature": 0.5,
        "system_prompt": f"You are a helpful and intelligent assistant. Always answer as helpfully as possible, while being safe. Analyze these docs of different functions and based on the input prompt, choose the best functions that we can use. Only provide the names of the functions that we have to use. This is the list explaining all the functions: {function_docs}. Only provide the names of the function in response. Don't give any other details.\n\n",
        "max_new_tokens": 1500,
        "min_new_tokens": -1
    }
    )
    output_1 = []
    for item in response_1:
        output_1.append(item)
    output_1 = "".join(output_1)

    function_codes = []

    for function in all_functions:
        function_codes.append(function["function_code"])


        
    function_names = []
    # all_func_names = []
    for function in function_docs:
        # all_func_names.append(function["function_name"])
        if function["function_name"] in output_1:
            function_names.append(function["function_name"])

    final_code = []
    all_codes = []
    for func in func_name_and_code:
        all_codes.append(func["function_code"])
        if func["function_name"] in function_names:
            final_code.append(func["function_code"])


    # Create a directory for the generated codes
    if not os.path.exists('generated_codes'):
        os.makedirs('generated_codes')

    # write import statements
    for imp in import_statements:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(imp)

    # write default functions.
    for def_func in default_functions:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(def_func) 


    for func in final_code:
        with open(f'generated_codes/code.py', 'a') as f:
            f.write(func+"\n")

    # save as
    with open(f'generated_codes/code.py', 'a') as f:
            f.write("\nbpy.ops.wm.save_as_mainfile(filepath='./generated_scene.blend')\n")
    

    command = ["C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe", "--background", "--python", "C:\\Users\\hp\\Documents\\FYP\\FYP-Backend\\generated_codes\\code.py"]
    # time.sleep(2)
    # Run the command
    subprocess.run(command)

    blend_file_path = "C:\\Users\\hp\\Documents\\FYP\\FYP-Backend\\generated_codes\\code.py"

 

    # return {
    #     "output_1":output_1, 
    #     "function_names": function_names,
    #     "all_code": all_codes,
        
   

    # }
    return FileResponse(blend_file_path, media_type="application/octet-stream")
        